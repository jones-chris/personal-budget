import logo from './logo.svg';
import './App.css';
import MenuBar from "./MenuBar/MenuBar";
import React, { Component } from "react";
import Transaction from "./Transaction/Transaction";
import Category from "./Category/Category";


class App extends Component {

    constructor() {
        super();

        this.state = {
          home: {
            hidden: false
          },
          transactions: {
            hidden: true
          },
          categories: {
            hidden: true
          }
        }
    }

    render() {
      return (
        <div className="App">
          <MenuBar setStateFunc={newState => this.setState(newState)}
                   state={this.state}
          />

          <Transaction hidden={this.state.transactions.hidden}
          />

          <Category hidden={this.state.categories.hidden}
          />
        </div>
      );
    }

} 

export default App;
