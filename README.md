# Multi-Agent Onboarding App (Azure AI Foundry Demo)

This is a demo project showcasing how to use **Azure AI Foundry Agent Service** to automate an employee onboarding flow using multiple AI agents.

## 🧠 What It Does

The app collects an employee's **full name**, **email**, and **department** from a simple frontend form. Behind the scenes, it dynamically creates and coordinates three agents:

- **`department_rag_agent`** – Uses Azure AI Search to retrieve relevant onboarding information about the specified department.
- **`discord_agent`** – Sends a welcome message to a Discord channel using the employee’s details and department info.
- **`onboarding_agent`** – Orchestrates the flow: first runs the RAG search, then delegates to the Discord agent to send the message.

> Agents are created, executed, and cleaned up on each request to keep everything stateless.

---

## 🧾 Required Azure Services

To run this app, you’ll need the following Azure resources:

- **Azure AI Foundry Project**  
  Used to create and coordinate the agents. You’ll use a deployed LLM (e.g., `gpt-4o-mini`) for agent reasoning and message generation.

- **Azure OpenAI**  
  Used to create and deploy the **embedding model** (e.g., `text-embedding-3-large`) for populating the vector index in Azure AI Search.

- **Azure AI Search**  
  Hosts the index with department-specific onboarding content.  
  👉 **Important:** You must connect your AI Search instance to your AI Foundry project.  
  [Learn how to connect it](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/connections-add?pivots=fdp-project)

- **Azure Function App**  
  Exposes an HTTP endpoint to send Discord messages via webhook. This is necessary because connected agents currently cannot call local Python functions directly.

---

## 📁 Project Structure

- `src/api/` – FastAPI backend with agent definitions, tools, and utilities
- `func-api/` – Azure Function App used to send messages to Discord
- `web/` – React.js frontend for submitting onboarding info
- `data/` – Contains department RAG source files (see below)

---

## 📄 Data for RAG

The file `software_engineering_dept.txt` located in the `/data` folder contains onboarding content for the Software Engineering department. This file is used to populate the Azure AI Search index and powers the department RAG query.

Make sure to:
- Embed the content using the `text-embedding-3-small` model
- Upload the embedded data into the index defined in your `.env` file

---

## ⚙️ .env Configuration

Create a `.env` file in `src/api/` with the following:

```env
# Azure AI Foundry
PROJECT_ENDPOINT=https://<your-foundry-endpoint>/api/projects/<project-name>
MODEL_DEPLOYMENT_NAME=<your-model-deployment-name>

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://<your-search-endpoint>
AZURE_SEARCH_API_KEY=<your-api-key>
AZURE_SEARCH_INDEX_NAME=<your-index-name>
