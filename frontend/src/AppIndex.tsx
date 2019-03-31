import * as React from 'react';
import './App.css';
import AppForm from './AppForm';
import AppQueue from './AppQueue';
import AppRecent from './AppRecent';

import logo from './logo.svg';

class AppIndex extends React.Component<{ history: any }, {}> {
  public render() {
    return (
      <div>
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Auto Debugger</h1>
        </header>
        <AppForm history={this.props.history} />
        <AppRecent />
        <AppQueue />
      </div>
    );
  }
}

export default AppIndex;
