# agency.py

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google, noise_cancellation
from prompt import agent_instruction, agent_response
from tools import get_weather, search_web, send_email  # ← Your tools

load_dotenv()


# ✅ Define your Assistant agent
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=agent_instruction,
            tools=[get_weather, search_web, send_email],  # ✅ Register tools here
        )


# ✅ Entrypoint for LiveKit Agent Worker
async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Aoede",
            temperature=0.8,
            instructions=agent_instruction,
        ),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),  # ← this now includes your tools!
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(instructions=agent_response)


# ✅ CLI entry to start the agent
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
