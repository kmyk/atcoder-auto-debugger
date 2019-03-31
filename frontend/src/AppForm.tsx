import * as React from 'react';
import './App.css';
import config from './config';

class AppForm extends React.Component<{ history: any }, { message: string, url: any }> {
  constructor(props: { history: any }) {
    super(props);
    this.handleClick = this.handleClick.bind(this);

    this.state = {
      message: "",
      url: React.createRef(),
    };
  }

  public render() {
    return (
      <div className="App-form">
        <div>{this.state.message}</div>
        <form>
          <input type="text" name="url" ref={this.state.url}  placeholder="https://atcoder.jp/contests/abc044/submissions/3367405" />
          <input type="button" onClick={this.handleClick} value="Submit" />
        </form>
      </div>
    );
  }

  private handleClick() {
    const params = new URLSearchParams();
    params.append("url", this.state.url.current.value);
    fetch(config.api + "analyze", {
        body: params,
        method: "POST",
    }).then((response) => {
      return response.json();
    }).then((json) => {
      if (json.id) {
        this.props.history.push("/result/" + json.id)
      } else {
        this.setState({ message: json.message });
      }
    });
  }
}

export default AppForm;
