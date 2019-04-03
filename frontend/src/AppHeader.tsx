import * as React from 'react';
import {Link} from 'react-router-dom';
import './App.css';

import logo from './logo.svg';

class AppIndex extends React.Component<{}, {}> {
  public render() {
    return (
      <header className="App-header">
        <Link to="/">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Auto Debugger</h1>
        </Link>
      </header>
    );
  }
}

export default AppIndex;
