import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { BrowserRouter, Route } from 'react-router-dom';
import AppIndex from './AppIndex';
import AppResult from './AppResult';
import './index.css';
import registerServiceWorker from './registerServiceWorker';

ReactDOM.render(
  (
    <BrowserRouter>
      <div className="App">
        <Route exact={true} path='/' component={AppIndex} />
        <Route path='/result/:id' component={AppResult} />
      </div>
    </BrowserRouter>
  ),
  document.getElementById('root') as HTMLElement
);
registerServiceWorker();
