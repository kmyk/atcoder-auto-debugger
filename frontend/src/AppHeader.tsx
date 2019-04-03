import * as React from 'react';
import './App.css';

import logo from './logo.svg';

class AppIndex extends React.Component<{}, {}> {
  public render() {
    return (
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1 className="App-title">Auto Debugger</h1>
      </header>
    );
  }
}

export default AppIndex;
