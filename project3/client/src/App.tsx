import React from "react";
import axios from "axios";
import { Resource, url } from "./Resource";
import "./App.css";

interface AppState {
  clientID: number;
}

class App extends React.Component<{}, AppState> {
  constructor(props: {}) {
    super(props);
    this.state = { clientID: -1 };
  }

  componentDidMount() {
    if (this.state.clientID === -1) {
      this.askClientID().then((clientID) => {
        this.setState({ ...this.state, clientID: clientID });
      });
    }
  }
  askClientID() {
    return axios
      .get<number>(`${url}/new_id`)
      .then((response) => {
        let clientID = response.data;
        console.log("clientID", clientID, response);
        return clientID;
      })
      .catch((reason) => {
        console.log(reason);
        return -1;
      });
  }

  render() {
    return (
      <div className="App">
        <div>Client ID: {this.state.clientID} </div>
        <div>
          <Resource resourceID={0} clientID={this.state.clientID} />
          <Resource resourceID={1} clientID={this.state.clientID} />
        </div>
      </div>
    );
  }
}

export default App;
