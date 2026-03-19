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
   * [  Attachments (0) ](/confluence/pages/viewpageattachments.action?pageId=246487098 "View Attachments")  
   * [  Page History ](/confluence/pages/viewpreviousversions.action?pageId=246487098)  
   * [  Page Information ](/confluence/pages/viewinfo.action?pageId=246487098)  
   * [  Resolved comments ](/confluence)  
   * [  View in Hierarchy ](/confluence/pages/reorderpages.action?key=one20en&openId=246487098#selectedPageInHierarchy)  
   * [  View Source ](/confluence/plugins/viewsource/viewpagesrc.action?pageId=246487098)  
   * [  Export to PDF ](/confluence/spaces/flyingpdf/pdfpageexport.action?pageId=246487098&atl%5Ftoken=4695ecadbdbff431e2a313590d43c758f3c68466)  
   * [  Export to Word ](/confluence/exportword?pageId=246487098)  
   * [   Copy Page Hierarchy ](/confluence/pages/viewpage.action?pageId=246487098&spaceKey=one20en)

[Manage control panels using gRPC API methods](/confluence/spaces/one20en/pages/246487098/Manage+control+panels+using+gRPC+API+methods) 

* Created by [Alina Luchkina](    /confluence/display/~alina.luchkina  
), last updated on [17.10.2022](/confluence/pages/diffpagesbyversion.action?pageId=246487098&selectedPageVersions=1&selectedPageVersions=2 "Show changes")  2 minute read

POST http://IP-address:port/prefix/grpc

**Get list of control panels**

Request body:

ListControlPanels(
               ListControlPanelsRequest(
                         view=VIEW_MODE_FULL
                            )
)

Response:

Click to expand

items {
  access_point: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
  display_id: "4"
  vendor: "Pelco-joystick"
  model: "KBD5000"
  properties {
    axes {
      key: "jog"
      value: "supportsContinuousJog"
    }
    axes {
      key: "pan"
      value: "supportsContinuousPan"
    }
    axes {
      key: "shuttle"
      value: "supportsContinuousShuttle"
    }
    axes {
      key: "tilt"
      value: "supportsContinuousTilt"
    }
    axes {
      key: "zoom"
      value: "supportsContinuousZoom"
    }
    buttons {
      value: "buttonFourPoint"
    }
    buttons {
      key: 1
      value: "buttonIris"
    }
    buttons {
      key: 2
      value: "buttonVision"
    }
    buttons {
      key: 3
      value: "buttonAbout"
    }
    buttons {
      key: 4
      value: "buttonInfo"
    }
    buttons {
      key: 5
      value: "buttonJoystickButton"
    }
    buttons {
      key: 8
      value: "buttonLeftFolder"
    }
    buttons {
      key: 9
      value: "buttonRightFolder"
    }
    buttons {
      key: 10
      value: "buttonPlayPause"
    }
    buttons {
      key: 11
      value: "buttonStop"
    }
    buttons {
      key: 12
      value: "buttonDelay"
    }
    buttons {
      key: 13
      value: "buttonOnePoint"
    }
    buttons {
      key: 14
      value: "buttonTwoPoint"
    }
    buttons {
      key: 15
      value: "buttonThreePoint"
    }
    buttons {
      key: 16
      value: "buttonNine"
    }
    buttons {
      key: 17
      value: "buttonZero"
    }
    buttons {
      key: 18
      value: "buttonVideo"
    }
    buttons {
      key: 19
      value: "buttonOneWindow"
    }
    buttons {
      key: 20
      value: "buttonFourWindow"
    }
    buttons {
      key: 21
      value: "buttonNineWindow"
    }
    buttons {
      key: 22
      value: "buttonSixteenWindow"
    }
    buttons {
      key: 23
      value: "buttonComputer"
    }
    buttons {
      key: 24
      value: "buttonOne"
    }
    buttons {
      key: 25
      value: "buttonTwo"
    }
    buttons {
      key: 26
      value: "buttonThree"
    }
    buttons {
      key: 27
      value: "buttonFour"
    }
    buttons {
      key: 28
      value: "buttonFive"
    }
    buttons {
      key: 29
      value: "buttonSix"
    }
    buttons {
      key: 30
      value: "buttonSeven"
    }
    buttons {
      key: 31
      value: "buttonEight"
    }
  }

  
**Get list of events**

Request body:

PullEvents(PullEventsRequest(filters=EventFilters(include=[EventFilter(subject="hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0",event_type=ET_ControlPanelStateEvent)])))

Response:

Click to expand

items {
  event_type: ET_ControlPanelStateEvent
  subject: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
  body {
    [type.googleapis.com/axxonsoft.bl.events.ControlPanelStateEvent] {
      guid: "c95204e2-1e63-47d4-ad43-c12ea7a4e928"
      object_id: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
      axes {
        name: "pan"
        value: -0.302052795887
      }
    }
  }
  subjects: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
}

items {
  event_type: ET_ControlPanelStateEvent
  subject: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
  body {
    [type.googleapis.com/axxonsoft.bl.events.ControlPanelStateEvent] {
      guid: "9a27d338-5280-4ae6-a686-a94181859cb9"
      object_id: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
      axes {
        name: "pan"
        value: -0.302052795887
      }
      axes {
        name: "tilt"
        value: 0.564027428627
      }
    }
  }
  subjects: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
}

items {
  event_type: ET_ControlPanelStateEvent
  subject: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
  body {
    [type.googleapis.com/axxonsoft.bl.events.ControlPanelStateEvent] {
      guid: "d8cec48a-99d9-4ee5-a24e-7aa59802760b"
      object_id: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
      axes {
        name: "pan"
        value: -0.726295232773
      }
      axes {
        name: "tilt"
        value: 0.564027428627
      }
    }
  }
  subjects: "hosts/Server1/DeviceIpint.4/EventSupplier.ioDevice:0"
}

* No labels

Overview

Content Tools

* Powered by [Atlassian Confluence](https://www.atlassian.com/software/confluence) 9.4.1
* Printed by Atlassian Confluence 9.4.1
* [Report a bug](https://support.atlassian.com/confluence-server/)
* [Atlassian News](https://www.atlassian.com/company)

[Atlassian](https://www.atlassian.com/)

{"serverDuration": 106, "requestCorrelationId": "6301baf71332876d"} 