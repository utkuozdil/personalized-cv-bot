import os
import openai

class OpenAIIntegration:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.model = model

    def embed_batch(self, texts: list) -> list:
        try:
            response = openai.embeddings.create(
                input=texts,
                model=self.model
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"OpenAI Batch Embedding Error: {e}")
            return [[] for _ in texts]

    def embed_query(self, query: str, model: str = "text-embedding-3-small") -> list:
        response = openai.embeddings.create(
            input=query,
            model=model
        )
        return response.data[0].embedding

    def chat(self, messages, model: str = "gpt-4-turbo", temperature: float = 0.2, max_tokens: int = 1000, stream: bool = True):
        try:
            if stream:
                response = openai.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )
                latest_reason = None
                for chunk in response:
                    delta = chunk.choices[0].delta
                    finish_reason = chunk.choices[0].finish_reason
                    content = getattr(delta, "content", None)
                    if finish_reason:
                        latest_reason = finish_reason
                    if content:
                        yield content, latest_reason
                if latest_reason is None:
                    yield None, "incomplete"
            else:
                # Non-streaming mode - return a direct response
                response = openai.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False
                )
                # Return the content and finish reason directly
                return response.choices[0].message.content, response.choices[0].finish_reason

        except Exception as e:
            print(f"OpenAI Chat Error: {e}")
            if stream:
                yield "⚠️ Error: Failed to stream response.", "error"
            else:
                return "⚠️ Error: Failed to generate response.", "error"

    def stream_to_string(self, messages, stream=False):
        try:
            if stream:
                # Streaming mode - collect tokens
                full_response = ""
                for token, _ in self.chat(messages, stream=True):
                    if token:  # Only add non-None tokens
                        full_response += token
                return full_response.strip()
            else:
                # Non-streaming mode - use the direct_chat method
                return self._direct_chat(messages)
        except Exception as e:
            print(f"Chat completion failed: {e}")
            return ""

    def _direct_chat(self, messages, model: str = "gpt-4-turbo", temperature: float = 0.2, max_tokens: int = 1000):
        """
        Direct method to get a chat completion without streaming.
        This method bypasses the generator handling and directly returns the content.
        """
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Direct Chat Error: {e}")
            return "⚠️ Error: Failed to generate response."

