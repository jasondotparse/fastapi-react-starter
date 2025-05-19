# Application overview of CHAI Agent Playground
This full stack web app is a simple playground in which a user can have a conversation with one or more CHAI characters. The user can choose to participate in the conversation or simply let the AI bot(s) chat amongst themselves. The user remains in control of the dialog turn progression and can interject at any time.

<img src="documentation/UI_screenshot.png" alt="UI Screenshot" width="50%">

## Getting started
### Running the app locally

#### Prerequisites
- Python (recommended version: >=3.11)
- Node.js (recommended version: >=v20)

#### Backend Setup

1. **Create and activate a Python virtual environment**:
   ```bash
   python -m venv .venv
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

2. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your CHAI AI key to the .env file** in the project root, update the .env and add your API key such that it looks like this:
   ```
   CHAI_API_BEARER_TOKEN="Bearer your_token_here"
   ```

4. **Start the FastAPI backend server**:
   ```bash
   python -m uvicorn app.main:app --reload --timeout-keep-alive 300
   ```

#### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd app/frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the React development server**:
   ```bash
   npm start
   ```

#### Accessing the Application

Once both servers are running:
- The frontend will be available at: http://localhost:3000
- The backend API will be available at: http://localhost:8000

#### Troubleshooting Tips

- If you encounter CORS issues, ensure both servers are running and the frontend is configured to connect to the correct backend URL.
- If you get authentication errors, check that your CHAI API token is correctly set in the .env file.
- If you're seeing a lot of 429 errors in the back end, this is due to throttling of the CHAI API.

## Application high level architecture:
### Front end 
Web UI: React.js based Typescript front end. It displays the chat history of the conversation, including all characters who have participated in the conversation, as well as a simple text field where the user can (optionally) add a <DialogTurn>, as well as a "Continue" button which, under the hood, invokes the back end POST /continueConversation API. The job of the front end is incredibly simple: Display the Conversation dialog turns, and provide an interface through which the user of the app can add DialogTurns to the conversation.

### Back end
Fully stateless FastAPI-based python server. It exposes 2 endpoints: 
1. initializeCharacters: This API is invoked at the start of a conversation, to generate a cast of AI agents which will List<Participant> (see section "data model" below) in the conversation.
2. continueConversation: At a high level, this simply takes in a <Conversation> (see section "data model" below) and returns an updated <Conversation> containing additional <DialogTurns> that encode the AI's response to the most recent <DialogTurn>. In this way, application state is held in the requests themselves, allowing the back end to be fully stateless. When a Conversation is sent from the back end to the front end, the front end can reply with an updated <Conversation> containing additional dialog turns, if the user chose to add a comment to the ongoing conversation. See section "Conversation flow" below.

This web app was forked from the fastapi-react-starter github package to reduce boilerplate setup.

## Data model 
<Conversation>
{
  participants: List<Participant>,
  dialogTurns: List<DialogTurn>
}

<Participant>
{
  type: String, // Enum: "HUMAN" or "AI",
  backstory?: String, // if not present (AKA, this is the first dialog turn), BE will generate it using LLM call
  name?: String, // if not present (AKA, this is the first dialog turn), BE will generate it using LLM call
}

<DialogTurn>
{
  participant: String, // must be one of the participant names in the conversation
  content: String // what was said by the participant in this particular dialog turn
}

## Back end API schema
### POST /initializeCharacters
input:
```
{
  count: Int // the number of AI characters to generate to participate in the conversation
  userEngagementEnabled: Boolean // indicates whether the user will be talking in the conversation, or if this is purely going to be a set of AI agents talking amongst themselves. 
}
```
output:
```
{
  participants: List<Participant>
}
```
### POST /continueConversation
input:
```
{
  conversation: <Conversation>
}
```
output:
```
{
  conversation: <Conversation>
}
```

## Data flow
Note: see the sequence diagrams in /documentation/sequence diagrams for a visual overview of several different conversation scenarios. The basic evolution of the <Conversation> is laid out below. 
1. web UI initializes the conversation by sending POST /initializeCharacters, providing the # of characters to initialize and a flag to indicate if the user wants to participate in the conversation.
2. back end generates the list of characters (names and backstories) and responds with List<Participant>. At this point, the client has all it needs to proceed to continue the conversation
3. The user optionally provides an input. If they do so, the front end adds a new <DialogTurn> to continueConversation. Then, the web UI calls POST /continueConversation, providing the (now longer) <Conversation>.
4. The back end chooses a character to speak next, and then generates a new <DialogTurn>. It adds this to the Conversation and sends it back to the UI.
* Steps 3 & 4 repeat until the user decides to end the session, or the prompt context window limit is reached. 

## LLM interface 
The back end leverages the publicly accessible API from CHAI. The following describes a POST endpoint exposing a stateless API to access one of our models via a chat interface.

### LLM API data model and usage example
> POST
http://guanaco-submitter.guanaco-backend.k2.chaiverse.com/endpoints/onsite/chat

Headers:
Authorization: "Bearer CR_14d43f2bf78b4b0590c2a8b87f354746"

JSON BODY:
{
    "memory": str,
    "prompt": str,
    "bot_name": str,
    "user_name": str,
    "chat_history": List[dict[str, str]]
}

Parameter explanations:
- memory: ** deprecated **
- prompt: This is the bot's prompt, which is truncated
          as the conversation progresses.
- bot_name: This is the name assigned to the character
            the model is acting as.
- user_name: This is the name assigned to agent interacting
             with the model.
- chat_history: This is a list of messages representing the
                conversation history. The format of each
                message is
                {
                    "sender": "sender_name",
                    "message": "some_string"
                }.

Example payload:
{
    "memory": "",
    "prompt": "An engaging conversation with Bot.",
    "bot_name": "Bot",
    "user_name": "User",
    "chat_history":
        [
          {"sender": "Bot", "message": "Hi there"},
          {"sender": "User", "message": "Hey Bot!"}
        ]
}
>
### LLM API key
Should be found in the .env file at the root of this project, under the name `CHAI_API_BEARER_TOKEN`. Example:
.env
```
CHAI_API_BEARER_TOKEN="Bearer abc123xyz456"
```

## Candiates for additional improvements/features
* Persistent storage. Since the app is stateless, the entire conversation history is erased with each restart of the back end. The Conversation object could be encoded as a pickle file or json.stringified and saved to a database in order to preserve conversation history easily. 
* Allow the customer to edit any individiual dialog turn, not just add new ones to the end of the Conversation.
* Back story customization: Instead of hard coding agents to be fantasy characters, allow the user to provide the "setting" in which the characters are generated, or furthermore, allow users to write their own agent backstories / descriptions.
* The back end logic for AI orchestration could be implemented in LangGraph, providing a neat node+edge-based agent communication paradigm, and allowing for easy extensibility with Tool Use. 
* Deploy the back end to a serverless function such as AWS Lambda, gated behind an AWS API Gateway, such that the web app could be accessed without requiring a locally running instance of the server. This would require only light refactoring of the service logic, since it was designed to be fully stateless. The web UI could be deployed by vending its web asset bundle via a simple AWS S3 bucket + Cloudfront CDN configuration.
* Allow for infinite conversation dialog turn length: instead of passing the entire conversation history in the CHAI API, only pass the most recent X number of dialog turns, such that the context window is never reached. To do this in such a way that characters don't "forget" about dialog turns outside their context window, prompt compression could be done via recursive summarization. 

## Appendix
### observations re: CHAI API
* The LLM doesn't appear to put much weight (if any?) on its "prompt" parameter. It can ignore information given in these prompts easily. The better way to load context into the LLM is by appending "background" information into the chat_history turns themselves. These can be hidden in the UI. 
* The request can take in more parameters than the documented provided in the Notion doc. These include "temperature" and "top_p", "max_output_tokens". Given these params, the request will respond with a 200, but it seemingly doesn't use them to alter the underlying LLM's input arguments, as the response contains the same fields in response.generation_params. This is annoying for character name generation, which would have a cleaner implementation if we could figure out a way to generate less deterministic outputs given the same LLM input. It also means the character name generator produces more characters than we need it to, slowing conversation initialization.
* The API is somewhat throttle-happy, meaning any prompt chains need to be implemented with a "cooldown" mechanism between LLM invocations. This is probably just a throttle applied to the provided API key... I assume these are given out for internal testing and are not the same APIs as they are obviously not serving the prod app. This is annoyning as it constrains the ability to use libraries like asyncio to fire off many requests at once and gather the responses. This limitation is most visible in the character backstory initialization sequence. 
* The API param chat_history.message.sender fields can contain names which are neither bot_name nor user_name. This opens the door to implement chat conversations which consist of more than 2 characters.
### additional notes on design decisions
* The Conversation state is held fully in the request / response schema between the back end and front end. I chose this paradigm for its simplicity and elegance, as despite the fact that it can grow indefinitely, the reality is that these requests / responses never grow to such a length that it is problematic from a web performance standpoint. 
* No LLM orchestration framework: since the functionalities of the back end chains / conversation orchestration are so simple, I decided not to add an additional dependency and use a framework like LangGraph or AutoGen.
### Unit test suite
#### running Backend tests
```bash
pytest
```

#### running Frontend tests
```bash
cd app/frontend
npm test
```
