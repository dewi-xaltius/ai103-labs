# Lab 17: Develop a Voice Live Agent

## Setup

1. Clone this repo (or download this lab folder) and open it in VS Code.

2. Set up a Python virtual environment:
   ```
   python -m venv labenv
   ```

3. Activate the virtual environment:
   ```
   .\labenv\Scripts\activate
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Open `.env` and replace each placeholder with your own values:

   | Variable | Where to find it |
   |---|---|
   | `AZURE_VOICELIVE_ENDPOINT` | Azure portal → your Foundry resource → Overview or Keys and Endpoint. Should look like `https://<resource-name>.services.ai.azure.com/api/projects/<project-name>` |
   | `AZURE_VOICELIVE_PROJECT_NAME` | The exact project name shown in Azure AI Foundry (case-sensitive) |
   | `AZURE_VOICELIVE_AGENT_ID` | The agent ID/name you created in the Agents tab of your Foundry project |

6. Authenticate with the Azure CLI (the client uses `AzureCliCredential`):
   ```
   az login
   ```
   Confirm you're on the correct subscription with `az account show`.

7. Run the client:
   ```
   python chat-client.py
   ```
