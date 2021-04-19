import React, { Component } from "react";
import Table from 'react-bootstrap/Table';


class Transaction extends Component {

	constructor(props) {
		super(props);

		this.state = {
			startDate: undefined,
			endDate: undefined,
			transactions: []
		}
	}

	/**
	* Get the default start date, which is the first day of the current month.
	*/
	getDefaultStartDate = () => {
		const today = new Date();

		let month;
		if (today.getMonth() + 1 < 10) {
			month = `0${today.getMonth() + 1}`;
		} else {
			month = `${today.getMonth() + 1}`;
		}

		let day = '01';

		let year = today.getFullYear();

		return `${month}/${day}/${year}`;
	}

	/**
	* Get the default end date, which is today.
	*/
	getDefaultEndDate = () => {
		const today = new Date();

		let month;
		if (today.getMonth() + 1 < 10) {
			month = `0${today.getMonth() + 1}`;
		} else {
			month = `${today.getMonth() + 1}`;
		}

		let day;
		if (today.getDate() < 10) {
			day = `0${today.getDate()}`;
		} else {
			day = today.getDate();
		}

		let year = today.getFullYear();

		return `${month}/${day}/${year}`;
	}

	getTransactions = () => {
		let startDate;
		if (this.state.startDate) {
			startDate = this.state.startDate;
		} else {
			startDate = this.getDefaultStartDate();
		}

		let endDate;
		if (this.state.endDate) {
			endDate = this.state.endDate;
		} else {
			endDate = this.getDefaultEndDate();
		}

		fetch(
            `http://localhost:5000/transactions?startDate=${startDate}&endDate=${endDate}`
		).then(response => response.json())
		 .then(responseJson => {
			let newState = {...this.state};
			newState.transactions = responseJson.transactions;
			this.setState(newState);
		 })

	}

	render() {
		if (!this.props.hidden) {
			if (this.state.transactions.length === 0) {
				this.getTransactions();
			}
		}

		// Create transactions JSX.
		let transactionsJsx = [];
		this.state.transactions.forEach(transaction => {
			transactionsJsx.push(
				<tr key={transaction.internal_id}>
					<td>{transaction.internal_id}</td>
					<td>{transaction.date}</td>
					<td>{transaction.payee}</td>
					<td>{transaction.amount}</td>
					<td>{transaction.institution_id}</td>
					<td>{transaction.checknum}</td>
					<td>{transaction.memo}</td>
					<td>{transaction.sic}</td>
					<td>{transaction.mcc}</td>
					<td>{transaction.type}</td>
				</tr>
			);
		});

		return (
			<div hidden={this.props.hidden.toString() === 'true'}>
				<Table striped bordered hover>
					<thead>
					    <tr>
					      <th>Internal ID</th>
					      <th>Date</th>
					      <th>Payee</th>
					      <th>Amount</th>
					      <th>Institution ID</th>
					      <th>Check Num</th>
					      <th>Memo</th>
					      <th>Sic</th>
					      <th>Mcc</th>
					      <th>Type</th>
					    </tr>
					  </thead>
					  <tbody>
					  	{transactionsJsx}
					  </tbody>
				</Table>
			</div>
		)
	}

}

export default Transaction;