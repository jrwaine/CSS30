import React from "react";
import axios from "axios";
import "./Resource.css";

interface ResourceProps {
  clientID: number;
  resourceID: number;
}

interface ResourceState {
  res: "Held" | "Asked" | "Released";
}

export const url = "http://localhost:8000";

export class Resource extends React.Component<ResourceProps, ResourceState> {
  constructor(props: ResourceProps) {
    super(props);
    this.state = { res: "Released" };
  }

  askResource = () => {
    if (this.state.res !== "Released") return;

    this.setState({ res: "Asked" });
    const events = new EventSource(
      `${url}/resource/${this.props.resourceID}/ask?client_id=${this.props.clientID}`
    );
    events.onmessage = (event) => {
      let msg = event.data;
      console.log("Received in ask", msg);
      if (msg === "Liberated") {
        this.setState({ res: "Held" });
        events.close();
      }
    };
  };

  releaseResource = () => {
    if (this.state.res !== "Held") return;
    axios
      .get<string>(`${url}/resource/${this.props.resourceID}/release`, {
        params: { client_id: this.props.clientID },
      })
      .then((response) => {
        console.log("released", this.props.resourceID);
        this.setState({ res: "Released" });
      })
      .catch((reason) => {
        console.log("error releasing", this.props.resourceID, reason);
        console.log("releasing", this.props.resourceID, "anyway");
        this.setState({ res: "Released" });
      });
  };

  render() {
    return (
      <div className="Resource">
        <div>Resource ID: {this.props.resourceID} </div>
        <div>Resource Status: {this.state.res} </div>
        <button className="ResourceButton" onClick={this.askResource}>
          Ask Resource
        </button>
        <button className="ResourceButton" onClick={this.releaseResource}>
          Release Resource
        </button>
      </div>
    );
  }
}
