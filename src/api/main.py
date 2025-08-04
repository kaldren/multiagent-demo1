from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ConnectedAgentTool, MessageRole, AgentThread
from utils.chat_utils import print_response
from models.onboarding_models import OnboardingModel
import os
import dotenv
import jsonref
import logging

from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType
from azure.ai.projects.models import ConnectionType


from azure.ai.agents.models import (
    OpenApiTool,
    OpenApiAnonymousAuthDetails,
)

dotenv.load_dotenv()

enabled_logging = True

project_endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

if enabled_logging:
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

@app.post("/api/onboard")
def onboard(onboard: OnboardingModel):
    result = None
    discord_agent = None
    department_rag_agent = None
    onboarding_agent = None
    thread: AgentThread

    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )

    # Define the Azure AI Search connection ID and index name
    azure_ai_conn_id = project_client.connections.get_default(ConnectionType.AZURE_AI_SEARCH).id

    index_name = "rag-1754232019406"

    # Initialize the Azure AI Search tool
    ai_search = AzureAISearchTool(
        index_connection_id=azure_ai_conn_id,
        index_name=index_name,
        query_type=AzureAISearchQueryType.VECTOR,
        top_k=3,
        filter="",
    )

    with project_client:
        with open(os.path.join(os.path.dirname(__file__), "discord.json"), "r") as f:
                openapi_discord = jsonref.loads(f.read())

        auth = OpenApiAnonymousAuthDetails()

        openapi_tool = OpenApiTool(
            name="FastAPI",
            spec=openapi_discord,
            description="API for Discord integration to send messages to a channel.",
            auth=auth
        )

        try:
            discord_agent = project_client.agents.create_agent(
                model=model_deployment_name,
                name="discord_agent",
                instructions='''You are responsible for sending welcome messages to a Discord channel using the tools you have.

            You will receive:
            - New employee details (full name and email)
            - Department-specific information retrieved from RAG

            Create a personalized welcome message that includes:
            1. A warm welcome greeting with the employee's full name
            2. Their email address for team reference
            3. Department-specific information to help them get started
            4. Any relevant onboarding details from the department information

            Format the message to be friendly, informative, and helpful for the new employee and existing team members.''',
                tools=openapi_tool.definitions
            )

            department_rag_agent = project_client.agents.create_agent(
                model=model_deployment_name,
                name="department_rag_agent",
                instructions='''You are responsible for retrieving relevant onboarding information about a specific department.

            Use the provided department name (e.g., "Software Engineering") to perform a RAG (Retrieval-Augmented Generation) search using your available tools.

            Return only useful onboarding content that helps a new employee get oriented within the department (e.g., team structure, tech stack, communication norms, useful links).

            Return it summarized in a meaningful way.''',
                tools=ai_search.definitions,
                tool_resources=ai_search.resources,
            )

            # Create connected agent tools for both agents
            discord_agent_tool = ConnectedAgentTool(
                id=discord_agent.id, name=discord_agent.name, description="Send a welcome message to Discord channel with new employee information.",
            )
            
            department_rag_agent_tool = ConnectedAgentTool(
                id=department_rag_agent.id, name=department_rag_agent.name, description="Search for department information to assist with onboarding",
            )

            # Combine both agent tools
            all_agent_tools = discord_agent_tool.definitions + department_rag_agent_tool.definitions

            onboarding_agent = project_client.agents.create_agent(
                model=model_deployment_name,
                name="onboarding_agent",
                instructions=
                    '''
                        You are an onboarding agent that coordinates the onboarding process of new employees.

                        When a new employee is onboarded, follow these steps:
                        1. First use the `department_rag_agent` to retrieve department-specific information for their department
                        2. Then use the `discord_agent` to send a welcome message that includes both the employee details (name, email) and the department information retrieved from RAG

                        Always get department information first before sending the Discord message.
                    ''',
                tools=all_agent_tools
            )

            thread = project_client.agents.threads.create()

            project_client.agents.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=f"New onboarding: {onboard.fullname} with email: {onboard.email} and department: {onboard.department}.",
            )

            project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=onboarding_agent.id)

            result = print_response(thread.id, project_client)

        except Exception as e:
            print(f"Error during onboarding: {e}")
            result = {"response": str(e)}

        finally:
            if discord_agent:
                project_client.agents.delete_agent(discord_agent.id)
            if department_rag_agent:
                project_client.agents.delete_agent(department_rag_agent.id)
            if onboarding_agent:
                project_client.agents.delete_agent(onboarding_agent.id)
            if thread:
                project_client.agents.threads.delete(thread.id)
            return {"response": result}