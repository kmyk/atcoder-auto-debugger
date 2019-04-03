import * as React from 'react';
import {UnControlled as CodeMirror} from 'react-codemirror2';
import './App.css';
import config from './config';

import 'codemirror/lib/codemirror.css';
import 'codemirror/mode/clike/clike';
import 'codemirror/theme/material.css';

import logo from './logo.svg';

class AppResult extends React.Component<{ match: any }, { id: number, result: any, editor: any }> {
  constructor(props: { match: any }) {
    super(props);

    this.state = {
      editor: null,
      id: parseInt(props.match.params.id, 10),
      result: null,
    };

    fetch(config.api + "result/" + this.state.id).then((response) => {
      return response.json();
    }).then((json) => {
      this.setState({ result: json });
      if (json.data) {
        for (const highlight of json.data.highlights) {
          this.state.editor.markText({line: highlight.lineno - 1, ch: 0}, {line: highlight.lineno - 1, ch: 9999}, {
            className: "CodeMirror-mark-" + highlight.level,
          });
        }
      }
    });
  }

  public render() {
    (console as any).log(this.state.result);
    if (this.state.result && ! this.state.result.data) {
      return (
        <div className="App-result">
          {this.state.result.message}
        </div>
      );
    }

    const options = {
      lineNumbers: true,
      mode: "text/x-c++src",
      readOnly: true,
    };
    const handleDidMount = (editor: any) => {
      this.setState({ editor })
      editor.setSize("100%", "100%");
    };

    return (
      <div className="App-result">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Auto Debugger</h1>
        </header>
        <h2>Source Code</h2>
        <CodeMirror value={ this.state.result && this.state.result.code } options={options} editorDidMount={handleDidMount} />
        <h2>Analyzed Result</h2>
        <ul>
          {
            this.state.result && this.state.result.data.checkboxes.map((message: string) => {
              return <li key={message}><label><input type="checkbox" />{message}</label></li>;
            })
          }
        </ul>
        <h2>Submission Info</h2>
        <table>
          <tbody>
            <tr><td>Source URL</td><td><a href={ this.state.result && this.state.result.url }>{ this.state.result && this.state.result.url }</a></td></tr>
            <tr><td>Task</td><td>{ this.state.result && this.state.result.name }</td></tr>
            <tr><td>User</td><td>{ this.state.result && this.state.result.user }</td></tr>
            <tr><td>Language</td><td>{ this.state.result && this.state.result.language }</td></tr>
            <tr><td>Status</td><td>{ this.state.result && this.state.result.status }</td></tr>
          </tbody>
        </table>
        {
          this.state.result && Object.keys(this.state.result.data.results).map((key: string) => {
            const value = this.state.result.data.results[key];
            return (
              <div key={key}>
                <h2><code><pre>$ {value.compiler} {value.options} main.cpp</pre></code></h2>
                <h3>Compile Error</h3>
                { value.compiler_stderr ? <CodeMirror value={value.compiler_stderr} options={options} /> : null }
                <h3>Test Cases</h3>
                <table>
                  <thead>
                    <tr><th>name</th><th>standard output</th><th>standard error</th></tr>
                  </thead>
                  <tbody>
                    {
                      value.sample_results && value.sample_results.map((sampleResult: any, serial: number) => {
                        return (
                          <tr key={key + "/" + (serial + 1)}>
                            <td>Sample {serial + 1}</td>
                            <td><CodeMirror value={sampleResult.stdout} options={options} /></td>
                            <td><CodeMirror value={sampleResult.stderr} options={options} /></td>
                          </tr>
                        );
                      })
                    }
                  </tbody>
                </table>
              </div>
            );
          })
        }
      </div>
    );
  }
}

export default AppResult;
