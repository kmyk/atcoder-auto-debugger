import * as React from 'react';
import './App.css';
import config from './config';

import logo from './logo.svg';

class AppResult extends React.Component<{ match: any }, { id: number, result: any }> {
  constructor(props: { match: any }) {
    super(props);

    const id = parseInt(props.match.params.id, 10);
    this.state = {
      id,
      result: null,
    };

    fetch(config.api + "result/" + id).then((response) => {
      return response.json();
    }).then((json) => {
      this.setState({ result: json });
    });
  }

  public render() {
    return (
      <div className="App-result">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Auto Debugger</h1>
        </header>
        <code><pre>{ this.state.result && this.state.result.code }</pre></code>
        <table>
          <tr><td>Source URL</td><td><a href={ this.state.result && this.state.result.url }>{ this.state.result && this.state.result.url }</a></td></tr>
          <tr><td>Task Name</td><td>{ this.state.result && this.state.result.name }</td></tr>
          <tr><td>User</td><td>{ this.state.result && this.state.result.user }</td></tr>
          <tr><td>Status</td><td>{ this.state.result && this.state.result.status }</td></tr>
          <tr><td>Language</td><td>{ this.state.result && this.state.result.language }</td></tr>
        </table>
      </div>
    );
  }
}

export default AppResult;
