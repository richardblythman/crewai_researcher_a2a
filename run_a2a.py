from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill, MissingAPIKeyError
from common.utils.push_notification_auth import PushNotificationSenderAuth
from taskmanager import AgentTaskManager
from agent import A2AWrapperAgent
import click
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", "host", default="0.0.0.0")
@click.option("--port", "port", default=10000)
def main(host, port):
    try:
        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
        skill = AgentSkill(
            id="simple_researcher_agent", 
            name="Simple Researcher Agent", 
            description="This agent uses CrewAI to research a topic", 
            tags=["a2a", "reasoning", "agent"], 
            examples=["do research on the topic 'AI'"], 
        )

        agent_card = AgentCard(
            name="Simple Researcher Agent", # TODO: Change this to the agent's name
            description="This agent uses CrewAI to research a topic", # TODO: Change this to the agent's description
            url= os.getenv("PROXY_URL", f"http://{host}:{port}/"),
            version="0.1.0",
            defaultInputModes=A2AWrapperAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=A2AWrapperAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        notification_sender_auth = PushNotificationSenderAuth()
        notification_sender_auth.generate_jwk()

        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(
                agent=A2AWrapperAgent(),
                notification_sender_auth=notification_sender_auth,
            ),
            host=host,
            port=port,
        )

        server.app.add_route(
            "/.well-known/jwks.json", notification_sender_auth.handle_jwks_endpoint, methods=["GET"]
        )

        logger.info(f"✅ Server running at http://{host}:{port}")
        server.start()

    except MissingAPIKeyError as e:
        logger.error(f"❌ Missing API Key: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"❌ Server startup error: {e}")
        exit(1)

if __name__ == "__main__":
    main()