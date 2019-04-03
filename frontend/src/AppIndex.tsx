import * as React from 'react';
import {Link} from 'react-router-dom';
import './App.css';
import AppForm from './AppForm';
import AppHeader from './AppHeader';
import config from './config';
import JudgeStatus from './JudgeStatus';

class AppIndex extends React.Component<{ history: any }, { queue: any[], recent: any[] }> {
  constructor(props: { history: any }) {
    super(props);
    this.state = { queue: [], recent: [] };

    fetch(config.api + "/queue").then((response) => {
      return response.json();
    }).then((json) => {
      this.setState({ queue: json });
    });

    fetch(config.api + "/recent").then((response) => {
      return response.json();
    }).then((json) => {
      this.setState({ recent: json });
    });
  }

  public render() {
    return (
      <div>
        <AppHeader />

        <h2>Submit</h2>
        <AppForm history={this.props.history} />

        <h2>Queue</h2>
        <table className="App-queue">
          <tbody>
            {
              this.state.queue.map((item: any) => {
                return (
                  <tr key={ item.id }>
                    <td>{ item.name }</td>
                    <td>{ item.user }</td>
                    <td><JudgeStatus status={ item.status } /></td>
                    <td>details</td>
                  </tr>
                );
              })
            }
          </tbody>
        </table>

        <h2>Recent Analyzed</h2>
        <table className="App-recent">
          <tbody>
            {
              this.state.recent.map((item: any) => {
                return (
                  <tr key={ item.id }>
                    <td>{ item.name }</td>
                    <td>{ item.user }</td>
                    <td><JudgeStatus status={ item.status } /></td>
                    <td><Link to={ "/result/" + item.id }>details</Link></td>
                  </tr>
                );
              })
            }
          </tbody>
        </table>
      </div>
    );
  }
}

export default AppIndex;
