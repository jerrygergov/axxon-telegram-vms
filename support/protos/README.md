Public gRPC API
---------------
The APIs defined here used both internally and by third party integrators, so it
is crucially important to maintain the high standard of quality, consistency and
backwards compatibility.

Contributing
------------
API design is governed by [Google API Improvement Proposals](https://google.aip.dev/general).
All changes must adhere to the AIPs and approved by two of the maintainers
before merge.

Most notable AIPs to read by all contributors:

 * [AIP-180 Backwards compatibility](https://google.aip.dev/180)
 * [AIP-181 Stability Levels](https://google.aip.dev/181)
 * [AIP-213 Common Components](https://google.aip.dev/213)
 * [AIP-215 Common Components Versions](https://google.aip.dev/215)
 * [AIP-200 Precedent](https://google.aip.dev/200) -- if an API violates the AIP standards for any reason

[Google Cloud APIs](https://github.com/googleapis/googleapis) is an excellent
source of inspiration and an example of how AIPs are applied in real
applications.

[AIP-200 Precedent](https://google.aip.dev/200) is important enough to mention
it separately. In situations when an API does not conform to AIP guides for any
reason: pre-existing functionality, requirement to follow an external
specification or work with existing system, a business need to deliver as soon
as possible, AIP-200 should be consulted and followed carefully.

Branches and versions
---------------------
The repository contains 3 main branches with their own stability guarantees as
per [AIP-181 Stability Levels](https://google.aip.dev/181):

|  Branch   | Alpha | Beta | Stable |
|-----------|-------|------|--------|
| minor     | X     | X    | X      |
| prestable |       | X    | X      |
| stable    |       |      | X      |

Each component is versioned separately, use separate version directories in
component subdirectory: i.e. events/v2/.

To allow for reasonable client and server backwards compatibility component
implementations must support at least two adjacent stable versions, for example
v3 and v4.

Maintainers
-----------
  * **Aleksandr Zagaevsky**
  * Oleg Malashenko
  * Anton Nikolaevsky
  * Evgeny Mironov

