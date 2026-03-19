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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487068 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487068)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487068)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487068#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487068)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487068&atl%5Ftoken=900dd9991a96c7d611e63611312f4952f5bcb93f)  
   * [  Export to Word ](/confluence/exportword?pageId=246487068)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487068&spaceKey=one20en)

[Bearer authorization](/confluence/spaces/one20en/pages/246487068/Bearer+authorization) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [17.10.2022](/confluence/pages/diffpagesbyversion.action?pageId=246487068&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  1 minute read

### **Receive a token**

Attention!

A direct gRPC request can be anonymous. If an HTTP request is made to a web server, then it is necessary to use the Basic authorization type, since the anonymous requests to the web server are prohibited.

Request body:

{
    "method": "axxonsoft.bl.auth.AuthenticationService.AuthenticateEx",
    "data": {
        "user_name" : "root",
        "password" : "root"
    }
}

Response example:

{
    "token_name": "auth_token",
    "token_value": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiIqLioiLCJleHAiOjE2MDUxOTIxMDcsImlhdCI6MTYwNTE3NzcwNywiaXNzIjoiVi1CRUxZQUtPViIsImxnbiI6InJvb3QiLCJybHMiOlsiOTc0NWI5MDItMmEzNi00MDM1LWJkZDYtMDEyZTBkYWU2NmMwIl0sInNpZCI6Ijk3YjA3ZWQ0LTEzOTctNGFiNC1iZjZiLWQwNTUwYmM1YjcwMSIsInN1YiI6IjMyOGUzODc0LTRhMzMtOWRkMS0yOWViLTQ0YzM3YTQ0MTIxYyJ9.nkqap2aosAafD41vPIICJjIaVCWwGnC1nZRFrPWkt8JpgUnQsxAaZMa1UwIdsTicnH9vWeq6laQgmRJagVnWcunjoJ6wHWptwfk-pGT49YE9V1_PMT_1f3wQoc8Hl5a118DXECQc2lcu56U0H74C9PBc2Xmh-8fbvaWws65y0Ly4rDbwEWdMd-0ocnnErpSiFOr-XEnok9PIVXo_mjgWsg1zxBlgijWqA4jVoQdfBvKzGpTFLxXgguDvCDZQyF3LfpxtjB1jNsZgaFHzxPkloLeq2eQ8TY2Y1g4BDDNW2QU-Ee-DhWoKIMrRWWhsbHLDMNC2sNpNVw0MMMEYSjDyng",
    "expires_at": "20201112T144147",
    "is_unrestricted": true,
    "user_id": "328e3874-4a33-9dd1-29eb-44c37a44121c",
    "roles_ids": [
        "9745b902-2a36-4035-bdd6-012e0dae66c0"
    ],
    "error_code": "AUTHENTICATE_CODE_OK"
}

where

**token\_value** − a Bearer token. The received token should be used in the metadata of the gRPC request. The HTTP requests should be made with the Bearer authorization type using the received token.

**expires\_at** − token expiration date and time in the UTC time zone.

### Renew a token

Request body:

{
	"method": "axxonsoft.bl.auth.AuthenticationService.RenewSession",
	"data":
	{		
	}
}

The response will be the same as the response to the receive token request.

Attention!

The token should be active at the time of the request.

### Close a token

Request body:

{
	"method": "axxonsoft.bl.auth.AuthenticationService.CloseSession",
	"data":
	{
	}
}

Response example:

{
    "error_code": "OK"
}

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 93, "requestCorrelationId": "78bd484cb8d9014f"} 