# ArcadeProvider

Get the player userId from the maimai arcade via the player QR code, and then get the score information.

Implementation: IPlayerProvider, IScoreProvider

Source: WahlapAimeServer, WahlapTitleServer

PyPi: https://pypi.org/project/maimai-ffi

## About open source

This part of `maimai.py` is not open source, we only distribute the compiled binary package on PyPi.

If you are using a device or architecture that is not supported, please contact us or open Issues on Github and we will try to resolve your issue as soon as possible.

## About security

It's not safe to make userId available to developers, and we want the userId to be used internally only.

We encrypt the player's userId with AES encryption, and decrypt it when calling the method, to keep the player's userId as secure as possible.

For more security suggestions, please contact us, we are committed to keeping player data safe and dedicated to maintaining the security of the maimai arcade servers.

# About proxy

Due to the network environment, some users may need to use a proxy to access the maimai arcade server. We provide a http_proxy parameter in the constructor to support the use of a proxy.

```python
from maimai import ArcadeProvider

provider = ArcadeProvider(http_proxy="http://127.0.0.1:7890")
```

## Disclaimer

Risk Notice:
This service needs to be connected to Wahlap AIME and title servers, and the default communication protocols and related obfuscation principles are derived from the Github open source repository, the developer has not used to analyze any game files. The Service may contain unknown logic errors, which may lead to potential risks such as data loss, system crash, etc. It is up to the user to decide whether to download and use the Service.

The service itself does not provide any intrusion, modification, capture other applications memory and network data, only the integration of major open-source projects to provide services for the user to choose, to facilitate the use of security analysts, to reduce the user's repetitive labor as well as management costs. Users can only use this service for formal learning and research or legally authorized application analysis, testing and other behavior, if the user in the process of using the software service against the above principles of loss to a third party, all the responsibility borne by the user.

Any organization or individual due to download and use of this service for any accident, negligence, contract damage, defamation, copyright or intellectual property infringement and its resulting losses (including but not limited to direct, indirect, incidental or consequential damages, etc.), the developer does not assume any legal responsibility. You may use the Service for commercial purposes, but only to extend the functionality or develop products through the features, interfaces or related services provided by the Service. You agree not to use the Service and its related services or interfaces for any purpose that violates local laws and regulations, or to engage in conduct that is detrimental to the interests of others.