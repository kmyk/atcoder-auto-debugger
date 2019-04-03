import * as React from 'react';
import { Link } from 'react-router-dom';
import './App.css';
import config from './config';

class AppRecent extends React.Component<{}, { data: any[] }> {

  constructor(props: {}) {
    super(props);
    this.state = { data: []  };
    fetch(config.api + "recent").then((response) => {
      return response.json();
    }).then((json) => {
      this.setState({ data: json });
    });
  }

  public render() {
    return (
      <table className="App-recent">
        <tbody>
          {
            this.state.data.map((item: any) => {
              return (
                <tr key={ item.id }>
                  <td>{ item.name }</td>
                  <td>{ item.user }</td>
                  <td>{ item.status }</td>
                  <td><Link to={ "/result/" + item.id }>details</Link></td>
                </tr>
              );
            })
          }
        </tbody>
      </table>
    );
  }
}

export default AppRecent;
