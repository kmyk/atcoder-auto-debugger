import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { HashRouter, Route } from 'react-router-dom';
import AppIndex from './AppIndex';
import AppResult from './AppResult';
import './index.css';
import registerServiceWorker from './registerServiceWorker';

ReactDOM.render(
  (
    <HashRouter>
      <div className="App">
        <Route exact={true} path='/' component={AppIndex} />
        <Route path='/result/:id' component={AppResult} />
      </div>
    </HashRouter>
  ),
  document.getElementById('root') as HTMLElement
);
registerServiceWorker();
