import logo from './logo.svg';
import './App.css';
import MenuBar from "./MenuBar/MenuBar";
import React, { Component } from "react";
import Transaction from "./Transaction/Transaction";
import Category from "./Category/Category";
import SplitTransactionModal from "./Modal/SplitTransactionModal";


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
          },
          splitTransactionModal: {
            hidden: true,
            transactionInternalId: null
          }
        }

        this.showSplitTransactionModal = this.showSplitTransactionModal.bind(this);
    }

    showSplitTransactionModal = (transactionInternalId) => {
      let newState = {...this.state};
      newState.splitTransactionModal.hidden = false;
      newState.splitTransactionModal.transactionInternalId = transactionInternalId;

      newState.transactions.hidden = true;

      this.setState(newState);
    }

    render() {
      return (
        <div className="App">
          <MenuBar setStateFunc={newState => this.setState(newState)}
                   state={this.state}
          />

          <Transaction hidden={this.state.transactions.hidden}
                       showSplitTransactionModalFunc={(transactionInternalId) => this.showSplitTransactionModal(transactionInternalId)}
          />

          <Category hidden={this.state.categories.hidden}
          />

          <SplitTransactionModal hidden={this.state.splitTransactionModal.hidden}
                                 transactionInternalId={this.state.splitTransactionModal.transactionInternalId}
          />
        </div>
      );
    }

} 

export default App;
