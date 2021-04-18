import logo from './logo.svg';
import './App.css';
import MenuBar from "./MenuBar/MenuBar";
import React, { Component } from "react";


// class App extends Component {

//     constructor() {
//         super();

//         this.state = {
            
//         }
//     }

// } 

function App() {
  return (
    <div className="App">
      <MenuBar/>

      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
