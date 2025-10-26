# aclarknet settings module.

from .base import *  # noqa
from pymongo.encryption_options import AutoEncryptionOpts
from bson import ObjectId

# Queryable Encryption
# INSTALLED_APPS += [  # noqa
#     "django_mongodb_backend",
#     "django_mongodb_demo",
# ]

# DATABASES["encrypted"] = {  # noqa
#     "ENGINE": "django_mongodb_backend",
#     "HOST": os.getenv("MONGODB_URI"),  # noqa
#     "NAME": "aclarknet_encrypted",
#     "OPTIONS": {
#         "auto_encryption_opts": AutoEncryptionOpts(
#             kms_providers={
#                 "local": {
#                     "key": b"tO\x7f\xf2L0\x9e\xab\xcd'\xd3\xd4'P\xf5;3\x94\xde8\xd7\xa4\xc5J\xe9\xb7\xc6\t\xbe\xa3<\xb3\xbe\xb3\xe5E\xb1\xdf[\xfb\x94\x8c`\x9e\xa20*\x82\x16\x98\xa32\x11\xa6\xeb\xfa\x05e\x08/\xe2\x01\xe8\xf1'#\xf9E\xde\xb0\x07Z\x93V\x84.\xf5\xb9\xdbR\xf6\xf6!\xd7;\xa9c\x087\xa1f\x9c\x1b\x86\xe8D"
#                 }
#             },
#             key_vault_namespace="aclarknet_encrypted.__keyVault",
#         ),
#     },
# }

# DATABASE_ROUTERS = ["aclarknet.routers.EncryptedRouter"]

# Sites framework
SITE_ID = ObjectId("000000000000000000000001")
SILENCED_SYSTEM_CHECKS = [
    "sites.E101",
]
INSTALLED_APPS += [
    "aclarknet.apps.MongoDBSitesConfig",
]

# Flatpages and Redirects
INSTALLED_APPS += [
    "aclarknet.apps.MongoDBFlatPagesConfig",
    "aclarknet.apps.MongoDBRedirectsConfig",
]
