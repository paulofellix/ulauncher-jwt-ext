import json
import logging
import base64
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

logger = logging.getLogger(__name__)

class JwtDecoderExtension(Extension):
    def __init__(self):
        logger.debug('Initializing JWT Decoder Extension')
        super(JwtDecoderExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        token = event.get_argument() or ""
        items = []
        logger.debug(f"Decoding JWT: {token}")
        try:
            # Split token into parts
            header, payload, signature = token.split('.')
            # Decode the header and payload from Base64 URL
            decoded_header = base64.urlsafe_b64decode(header + '==').decode('utf-8')
            decoded_payload = base64.urlsafe_b64decode(payload + '==').decode('utf-8')
            
            # Convert to JSON for pretty print
            header_json = json.loads(decoded_header)
            payload_json = json.loads(decoded_payload)

             # Create one JSON blob containing header, payload, and signature
            jwt_json = {
                "header": header_json,
                "payload": payload_json,
                "signature": signature
            }
            items.append(ExtensionResultItem(icon='images/jwt.svg',
                                                name=f"{json.dumps(jwt_json, indent=2)}",
                                                on_enter=CopyToClipboardAction(json.dumps(jwt_json, indent=2))))
            
        except Exception as e:
            items.append(ExtensionResultItem(icon='images/jwt.svg',
                                                name=f"Invalid JWT: {str(e)}",
                                                description='Error decoding JWT',
                                                on_enter=HideWindowAction()))
        return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        return RenderResultListAction([ExtensionResultItem(icon='images/jwt.svg',
                                                           name=data.get('new_name', 'No data available'),
                                                           on_enter=HideWindowAction())])

if __name__ == '__main__':
    logger.debug('Starting JWT Decoder Extension')
    JwtDecoderExtension().run()
