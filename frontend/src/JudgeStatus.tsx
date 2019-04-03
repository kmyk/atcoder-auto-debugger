import * as React from 'react';
import './App.css';

class AppIndex extends React.Component<{ status: string }, {}> {
  public render() {
    const className = "JudgeStatus-" + (this.props.status === "AC" ? "success" : "failure");
    return <span className={ className }>{ this.props.status }</span>;
  }
}

export default AppIndex;
