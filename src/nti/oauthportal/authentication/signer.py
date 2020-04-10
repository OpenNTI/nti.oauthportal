from nti.common.interfaces import IContentSigner
from nti.common.model import ContentSigner


def includeme(config):
    settings = config.registry.settings
    signer = ContentSigner(settings['signer.secret'],
                           settings['signer.salt'])
    config.registry.registerUtility(signer, IContentSigner)
