import * as React from 'react';
import './App.css';
import config from './config';

class AppQueue extends React.Component<{}, { data: any[] }> {

  constructor(props: {}) {
    super(props);
    this.state = { data: []  };
    fetch(config.api + "queue").then((response) => {
      return response.json();
    }).then((json) => {
      this.setState({ data: json });
    });
  }

  public render() {
    return (
      <table className="App-queue">
        <tbody>
          {
            this.state.data.map((item: any) => {
              return (
                <tr key={ item.id }>
                  <td>{ item.name }</td>
                  <td>{ item.user }</td>
                  <td>{ item.status }</td>
                  <td><a href={ "/result/" + item.id }>details</a></td>
                </tr>
              );
            })
          }
        </tbody>
      </table>
    );
  }
}

export default AppQueue;
