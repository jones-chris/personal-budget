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
            transactionId: null,
            transactionCategoryId: null
          }
        }

        this.showSplitTransactionModal = this.showSplitTransactionModal.bind(this);
    }

    showSplitTransactionModal = (transactionId, transactionCategoryId) => {
      let newState = {...this.state};
      newState.splitTransactionModal.hidden = false;
      newState.splitTransactionModal.transactionId = transactionId;
      newState.splitTransactionModal.transactionCategoryId = transactionCategoryId;

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
                       showSplitTransactionModalFunc={(transactionId, transactionCategoryId) => this.showSplitTransactionModal(transactionId, transactionCategoryId)}
          />

          <Category hidden={this.state.categories.hidden}
          />

          <SplitTransactionModal hidden={this.state.splitTransactionModal.hidden}
                                 transactionId={this.state.splitTransactionModal.transactionId}
                                 transactionCategoryId={this.state.splitTransactionModal.transactionCategoryId}
          />
        </div>
      );
    }

} 

export default App;
