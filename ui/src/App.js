import logo from './logo.svg';
import './App.css';
import MenuBar from "./MenuBar/MenuBar";
import React, { Component } from "react";
import Transaction from "./Transaction/Transaction";
import Category from "./Category/Category";
import SplitTransactionModal from "./Modal/SplitTransactionModal";
import Reports from "./Reports/Reports";


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
          },
          reports: {
            hidden: true
          }
        }

        this.showSplitTransactionModal = this.showSplitTransactionModal.bind(this);
        this.hideSplitTransactionModal = this.hideSplitTransactionModal.bind(this);
    }

    showSplitTransactionModal = (transactionId, transactionCategoryId) => {
      let newState = {...this.state};
      newState.splitTransactionModal.hidden = false;
      newState.splitTransactionModal.transactionId = transactionId;
      newState.splitTransactionModal.transactionCategoryId = transactionCategoryId;

      newState.transactions.hidden = true;

      this.setState(newState);
    }

    hideSplitTransactionModal = () => {
      let newState = {...this.state};
      newState.splitTransactionModal.hidden = true;
      newState.splitTransactionModal.transactionId = null;
      newState.splitTransactionModal.transactionCategoryId = null;

      newState.transactions.hidden = false;

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
                                 onCloseModalHandler={this.hideSplitTransactionModal}
          />

          <Reports hidden={this.state.reports.hidden}
          />
        </div>
      );
    }

} 

export default App;
