import os
import time
from dotenv import load_dotenv

# import namespaces for async
import asyncio
from openai import AsyncOpenAI
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider


# DEMO: each prompt is sent to the model THREE times, each with different
# instructions. The three requests run at the same time (concurrently).
# They're listed longest-answer-first on purpose: the "Deep dive" request is
# SENT first but will usually FINISH last, which shows the calls overlapping.
PERSPECTIVES = {
    "Deep dive": "You are a helpful AI assistant. Give a detailed, well-structured answer, including pros and cons where relevant.",
    "Beginner":  "You are a helpful AI assistant. Explain the answer for a complete beginner in one short paragraph.",
    "One-liner": "You are a helpful AI assistant. Answer in exactly one sentence.",
}


async def ask(async_client, model_deployment, label, instructions, input_text, previous_id, batch_start):
    """Send ONE request and report when it was sent and when it finished."""
    sent = time.perf_counter() - batch_start
    print(f"  -> [{sent:5.2f}s] Sent '{label}' request")

    # 'await' pauses THIS task only - the other requests keep running meanwhile
    response = await async_client.responses.create(
        model=model_deployment,
        instructions=instructions,
        input=input_text,
        previous_response_id=previous_id
    )

    done = time.perf_counter() - batch_start
    return label, response, sent, done


async def main():

    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    credential = None
    async_client = None

    try:
        # Get configuration settings
        load_dotenv()
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Initialize an async OpenAI client
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential, "https://ai.azure.com/.default"
        )

        async_client = AsyncOpenAI(
            base_url=azure_openai_endpoint,
            api_key=token_provider
        )

        # Track responses - one conversation thread per perspective
        last_response_ids = {label: None for label in PERSPECTIVES}

        # Loop until the user wants to quit
        while True:
            input_text = input('\nEnter a prompt (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue

            print("\nSending all requests at once...")
            batch_start = time.perf_counter()

            # Create one task per perspective - none of them has run yet
            tasks = [
                ask(async_client, model_deployment, label, instructions,
                    input_text, last_response_ids[label], batch_start)
                for label, instructions in PERSPECTIVES.items()
            ]

            # as_completed() starts them all together and hands back each
            # result as soon as it is ready - in FINISH order, not SEND order
            call_durations = []
            finish_position = 0
            for next_finished in asyncio.as_completed(tasks):
                label, response, sent, done = await next_finished
                finish_position += 1
                call_durations.append(done - sent)
                last_response_ids[label] = response.id

                print(f"\n#{finish_position} finished: {label}  "
                      f"(sent {sent:.2f}s, done {done:.2f}s, took {done - sent:.2f}s)")
                print("-" * 60)
                print(response.output_text)

            # The key comparison
            total_time = time.perf_counter() - batch_start
            print("\n" + "=" * 60)
            print(f"Total wall-clock time (async, concurrent): {total_time:.2f}s")
            print(f"Sum of individual call times:              {sum(call_durations):.2f}s"
                  "  <- roughly what synchronous code would take")
            print("=" * 60)

    except Exception as ex:
        print(ex)

    finally:
        # Close the async client session and credential
        if async_client:
            await async_client.close()
        if credential:
            await credential.close()


if __name__ == '__main__':
    asyncio.run(main())


