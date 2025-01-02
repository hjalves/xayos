import ignition
from cryptography.utils import CryptographyDeprecationWarning

import warnings

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# Fetch capsule content
response = ignition.request("//geminiprotocol.net/")

# Get status from remote capsule
print(response.status)

# Get response information from remote capsule
print(response.data())
