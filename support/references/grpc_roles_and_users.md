[Axxon One 2.0 (english)](/confluence/spaces/one20en/pages/246484043/Documentation "Axxon One 2.0 (english)")Edit space details

[](/confluence/spaces/ASdoc/pages/84353171/AxxonSoft+documentation+repository "AxxonSoft documentation repository")   
[Go to documentation repository](/confluence/spaces/ASdoc/pages/84353171/AxxonSoft+documentation+repository "AxxonSoft documentation repository")

[Contact technical support](https://support.axxonsoft.com/)  

Search 

## Page tree

[](/confluence/collector/pages.action?key=one20en)

Browse pages

ConfigureSpace tools[](#)

Previous page Next page

* Jira links

* [ ](#)  
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487062 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487062)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487062)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487062#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487062)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487062&atl%5Ftoken=5e9bb446d0488af1fb6f5dbfcd7179c72920c087)  
   * [  Export to Word ](/confluence/exportword?pageId=246487062)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487062&spaceKey=one20en)

[Roles and Users](/confluence/spaces/one20en/pages/246487062/Roles+and+Users) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated by [Yulia Morozova](    /confluence/display/~yulia.morozova  
) on [30.01.2024](/confluence/pages/diffpagesbyversion.action?pageId=246487062&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  3 minute read

[General information about users](/confluence/spaces/one20en/pages/246485139/General+information+about+users)

[Manage users using gRPC API methods](/confluence/spaces/one20en/pages/246487088/Manage+users+using+gRPC+API+methods)

Roles and users operation is described by three proto-files:

1. **SecurityService.proto** contains the objects definition, their properties and methods.
2. **GlobalPermissions.proto** contains the properties of the global access parameters.
3. **ObjectsPermissions.proto** contains the parameters properties to access the specific objects.

Methods in **SecurityService.proto**:

* message **ListConfigRequest** − request the configuration.
* message **ChangeConfigRequest** − create/edit/delete the configuration.
* message **ListGlobalPermissionsRequest** − request the global access parameters.
* message **SetGlobalPermissionsRequest** − set the global access parameters.
* message **ListObjectPermissionsRequest** − request the parameters to access the specific objects.
* message **SetObjectPermissionsRequest** − set the parameters to access the specific objects.

Properties in **SecurityService.proto**:

Expand...

The [Role ](/confluence/spaces/one20en/pages/246485141/Roles)object (message Role):

| Property     | Description                            |
| ------------ | -------------------------------------- |
| index        | GUID                                   |
| name         | Role name                              |
| comment      | Comment                                |
| timezone\_id | The ID of the role operation time zone |

The simultaneous connections limit (message ConnectionRestrictions):

| Property      | Description                              |
| ------------- | ---------------------------------------- |
| web\_count    | Maximum number of web app connections    |
| mobile\_count | Maximum number of mobile app connections |

The **[User](/confluence/spaces/one20en/pages/246485152/Configuring+local+users)** object (message User):

| Property                            | Description                                                    |
| ----------------------------------- | -------------------------------------------------------------- |
| index                               | GUID                                                           |
| loginname                           | User name                                                      |
| comment                             | Comment                                                        |
| date\_created                       | Date of creation                                               |
| date\_expires                       | Sertificate expiration date                                    |
| enabled                             | Is activated                                                   |
| ldap\_server\_id                    | LDAP Server ID                                                 |
| ldap\_domain\_name                  | LDAP Server Name                                               |
| ConnectionRestrictions restrictions | A set of message ConnectionRestrictions properties (see above) |

The user and role connection (message UserAssignment):

| Property | Description |
| -------- | ----------- |
| user\_id | User id     |
| role\_id | Role id     |

The [LDAP](/confluence/spaces/one20en/pages/246485146/LDAP+catalogs) object (message LDAPServer):

| Property         | Description                 |
| ---------------- | --------------------------- |
| index            | GUID                        |
| server\_name     | Server name or IP adress    |
| friendly\_name   | Name                        |
| port             | Port                        |
| base\_dn         | Base DN                     |
| login            | User                        |
| password         | Password                    |
| use\_ssl         | Use secure connection (SSL) |
| search\_filter   | Search filter               |
| login\_attribute | Login attribute             |
| dn\_attribute    | DN attribute                |

Properties in **GlobalPermissions.proto**:

Expand...

The PTZ control priority (enum ETelemetryPriority):

| Property                         | Description                               |
| -------------------------------- | ----------------------------------------- |
| TELEMETRY\_PRIORITY\_UNSPECIFIED | The PTZ control priority is not specified |
| TELEMETRY\_PRIORITY\_NO\_ACCESS  | No access                                 |
| TELEMETRY\_PRIORITY\_LOWEST      | Minimum level                             |
| TELEMETRY\_PRIORITY\_LOW         | Low level                                 |
| TELEMETRY\_PRIORITY\_NORMAL      | Medium level                              |
| TELEMETRY\_PRIORITY\_HIGH        | High level                                |
| TELEMETRY\_PRIORITY\_HIGHEST     | Maximum level                             |

The map access (enum EMapAccess):

| Property                 | Description                     |
| ------------------------ | ------------------------------- |
| MAP\_ACCESS\_UNSPECIFIED | The map access is not specified |
| MAP\_ACCESS\_FORBID      | The map access is forbidden     |
| MAP\_ACCESS\_VIEW\_ONLY  | You can only view maps          |
| MAP\_ACCESS\_VIEW\_SCALE | You can move and scale maps     |
| MAP\_ACCESS\_FULL        | All options available           |

The features access (enum EFeatureAccess):

| Property                                                 | Description                                                                                                                                                                          |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| FEATURE\_ACCESS\_FORBID\_ALL                             | All features are forbidden                                                                                                                                                           |
| FEATURE\_ACCESS\_DEVICES\_SETUP                          | Device settings (see [Devices](/confluence/spaces/one20en/pages/246484229/Devices))                                                                                                  |
| FEATURE\_ACCESS\_ARCHIVES\_SETUP                         | Archive settings (see [Archive](/confluence/spaces/one20en/pages/246484555/Archive))                                                                                                 |
| FEATURE\_ACCESS\_DETECTORS\_SETUP                        | Detection settings (see [Detectors](/confluence/spaces/one20en/pages/246484616/Detectors))                                                                                           |
| FEATURE\_ACCESS\_USERS\_RIGHTS\_SETUP                    | User permission settings (see [General information about users](/confluence/spaces/one20en/pages/246485139/General+information+about+users))                                         |
| FEATURE\_ACCESS\_CHANGING\_LAYOUTS                       | Editing layouts (see [Configuring layouts](/confluence/spaces/one20en/pages/246485172/Configuring+layouts))                                                                          |
| FEATURE\_ACCESS\_EXPORT                                  | Exporting snapshots and video recordings (see [Exporting frames and video recordings](/confluence/spaces/one20en/pages/246486422/Exporting+frames+and+video+recordings))             |
| FEATURE\_ACCESS\_LAYOUTS\_TAB                            | Access to Layouts tab (see [Layouts management](/confluence/spaces/one20en/pages/246486323/Layouts+management))                                                                      |
| FEATURE\_ACCESS\_SETTINGS\_SETUP                         | Options settings (see [System preferences](/confluence/spaces/one20en/pages/246485409/System+preferences))                                                                           |
| FEATURE\_ACCESS\_MINMAX\_BUTTON\_ALLOWED                 | Minimizing the Client to the system tray (see [Interface of Axxon One](/confluence/spaces/one20en/pages/246484112/Interface+of+Axxon+One))                                           |
| FEATURE\_ACCESS\_SYSTEM\_JOURNAL                         | Viewing the system log (see [System log](/confluence/spaces/one20en/pages/246486490/System+log))                                                                                     |
| FEATURE\_ACCESS\_DOMAIN\_MANAGING\_OPS                   | Managing an Axxon domain (see [Axxon Domain operations](/confluence/spaces/one20en/pages/246484230/Configuring+domains))                                                             |
| FEATURE\_ACCESS\_ADD\_CAMERA\_TO\_LAYOUT\_IN\_MONITORING | Adding a camera to a layout in live video mode (see [Adding cameras to cells](/confluence/spaces/one20en/pages/246485213/Adding+cameras+to+cells))                                   |
| FEATURE\_ACCESS\_SEARCH                                  | Archive search (see [Video surveillance in the Archive Search mode](/confluence/spaces/one20en/pages/246486140/Video+surveillance+in+the+Archive+Search+mode))                       |
| FEATURE\_ACCESS\_EDIT\_PTZ\_PRESETS                      | Adding and editing presets for PTZ cameras (see [Control Using the Presets List](/confluence/pages/viewpage.action?pageId=150075773))                                                |
| FEATURE\_ACCESS\_PROGRAMMING\_SETUP                      | Programming setup (see [Programming](/confluence/spaces/one20en/pages/246485013/Programming))                                                                                        |
| FEATURE\_ACCESS\_WEB\_UI\_LOGIN                          | Access to the Web server (see [Working with Axxon One through the Web-Client](/confluence/spaces/one20en/pages/246486507/Working+with+Axxon+One+through+the+Web-Client))             |
| FEATURE\_ACCESS\_COMMENT                                 | User comments for recorded video (see [Operator comments](/confluence/spaces/one20en/pages/246485868/Operator+comments))                                                             |
| FEATURE\_ACCESS\_ALLOW\_BUTTON\_MENU\_CAMERA             | Context menu of a video camera in a viewing tile (see [Context Menu of the Surveillance window](/confluence/spaces/one20en/pages/246485706/Context+Menu+of+the+Surveillance+window)) |
| FEATURE\_ACCESS\_ALLOW\_SHOW\_TITLES                     | Displaying captions (see [Viewing titles from POS terminals](/confluence/spaces/one20en/pages/246485885/Viewing+titles+from+POS+terminals))                                          |
| FEATURE\_ACCESS\_SHOW\_ERROR\_MESSAGES                   | Show error messages (see [Event control](/confluence/spaces/one20en/pages/246486484/Event+control))                                                                                  |

Alarms Management (enum EAlertAccess):

| Property                   | Description                                                |
| -------------------------- | ---------------------------------------------------------- |
| ALERT\_ACCESS\_UNSPECIFIED | The alarms access is not specified                         |
| ALERT\_ACCESS\_FORBID      | Users have no access to alarm videos                       |
| ALERT\_ACCESS\_VIEW\_ONLY  | Users can view alarm videos but they can't evaluate alarms |
| ALERT\_ACCESS\_FULL        | Users can view alarm videos and evaluate alarms            |

Unlimited access to all features (enum EUnrestrictedAccess):

| Property                          | Description                       |
| --------------------------------- | --------------------------------- |
| UNRESTRICTED\_ACCESS\_UNSPECIFIED | Unlimited access is not specified |
| UNRESTRICTED\_ACCESS\_NO          | Unlimited access is forbidden     |
| UNRESTRICTED\_ACCESS\_YES         | Unlimited access to all features  |

Properties in **ObjectsPermissions.proto**:

Expand...

The video camera access (enum ECameraAccess):

| Property                                    | Description                                                                                      |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| CAMERA\_ACCESS\_UNSPECIFIED                 | The video camera access is not specified                                                         |
| CAMERA\_ACCESS\_FORBID                      | You cannot access the device                                                                     |
| CAMERA\_ACCESS\_MONITORING\_ON\_PROTECTION  | You can view video from the camera only when the camera is armed                                 |
| CAMERA\_ACCESS\_MONITORING                  | You can live video from the camera. Other functions and device configuration are not available   |
| CAMERA\_ACCESS\_ARCHIVE                     | You can view live and recorded video from the camera. You cannot arm/disarm/configure the camera |
| CAMERA\_ACCESS\_MONITORING\_ARCHIVE\_MANAGE | All functions available. You cannot configure the device                                         |
| CAMERA\_ACCESS\_FULL                        | All functions and settings available                                                             |

The microphone access (enum EMicrophoneAccess):

| Property                        | Description                                                                                                                                                          |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MICROPHONE\_ACCESS\_UNSPECIFIED | The microphone access is not specified                                                                                                                               |
| MICROPHONE\_ACCESS\_FORBID      | The user is unable to listen to live sound from the video camera. The user is unable to listen to sound recordings from the archive                                  |
| MICROPHONE\_ACCESS\_MONITORING  | The user is able to listen to live sound from the video camera (the microphone must be turned on). The user is unable to listen to sound recordings from the archive |
| MICROPHONE\_ACCESS\_FULL        | All functions are accessible                                                                                                                                         |

The PTZ access (enum ETelemetryAccess):

| Property                       | Description                           |
| ------------------------------ | ------------------------------------- |
| TELEMETRY\_ACCESS\_UNSPECIFIED | The PTZ access is not specified       |
| TELEMETRY\_ACCESS\_FORBID      | The user cannot control pan/tilt/zoom |
| TELEMETRY\_ACCESS\_CONTROL     | The user can control pan/tilt/zoom    |

The archive access (enum EArchiveAccess):

| Property                     | Description                            |
| ---------------------------- | -------------------------------------- |
| ARCHIVE\_ACCESS\_UNSPECIFIED | The archive access is not specified    |
| ARCHIVE\_ACCESS\_FORBID      | Access is not provided to this archive |
| ARCHIVE\_ACCESS\_FULL        | Archive is available for all functions |

The video walls access (EVideowallAccess):

| Property                       | Description                             |
| ------------------------------ | --------------------------------------- |
| VIDEOWALL\_ACCESS\_UNSPECIFIED | The video walls access is not specified |
| VIDEOWALL\_ACCESS\_FORBID      | The access is forbidden                 |
| VIDEOWALL\_ACCESS\_FULL        | The access is granted                   |

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 221, "requestCorrelationId": "1515de82f34187e2"} 