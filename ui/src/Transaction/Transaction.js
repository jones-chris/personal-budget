import React, { Component } from "react";
import Table from 'react-bootstrap/Table';
import Button from "react-bootstrap/Button";
import './Transaction.css';


class Transaction extends Component {

	constructor(props) {
		super(props);

		this.state = {
			initialized: false,
			startDate: undefined,
			endDate: undefined,
			transactions: [],
			categories: []
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

		return `${year}-${month}-${day}`;
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

		return `${year}-${month}-${day}`;
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

	getCategories = () => {
		fetch(
            'http://localhost:5000/categories'
		).then(response => response.json())
		 .then(responseJson => {
			let newState = {...this.state};
			newState.categories = responseJson;
			this.setState(newState);
		 })
	}

	onUpdateCategory = async (transactionId, categoryId, amount, transactionCategoryId) => {
		// Don't do anything if categoryId is null, undefined, or empty string.
		if (categoryId === undefined || categoryId === null || categoryId === '') {
			return;
		}

		const response = await fetch(
			`http://localhost:5000/transaction/category/${transactionCategoryId}`,
			{
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(
					[
						{
							id: transactionCategoryId, 
							category_id: categoryId,
							transaction_id: transactionId,
							amount: amount
						}
					]
				)
			}
		)

		if (response.status === 200) {
			this.getTransactions();
		} else {
			let responseJson = response.json();
			
			console.log(responseJson);

			alert('There was an error updating the transaction category');
		}
	}

	render() {
		if (! this.props.hidden) {
			if (! this.state.initialized) {
				this.getTransactions();
				this.getCategories();
				
				this.setState({...this.state, initialized: true})
			}
		}

		// Create transactions JSX.
		let transactionsJsx = [];
		this.state.transactions.forEach(transaction => {
			// Create categories options JSX.
			let categoriesJsx = [];
			this.state.categories.forEach(category => {
				categoriesJsx.push(
					<option value={category.id} selected={transaction.category_id === category.id}>{category.name}</option>
				)
			});


			// Create transaction row using categories options JSX.
			const transactionId = transaction.id;
			const transactionAmount = (transaction.amount) ? transaction.amount : transaction.transaction_amount;
			const transactionCategoryId = transaction.transaction_category_id;
			transactionsJsx.push(
				<tr key={transaction.id + '-' + transaction.transaction_category_id}>
					<td hidden>{transaction.id}</td>
					<td>{transaction.date}</td>
					<td>{transaction.payee}</td>
					<td>{transactionAmount}</td>
					<td>{transaction.institution_id}</td>
					<td>
						<select onChange={(event) => this.onUpdateCategory(transactionId, event.target.value, transactionAmount, transactionCategoryId)}>
							<option value=""></option>
							{categoriesJsx}
						</select>
					</td>
					<td>{transaction.checknum}</td>
					<td>{transaction.memo}</td>
					<td>{transaction.sic}</td>
					<td>{transaction.mcc}</td>
					<td>{transaction.type}</td>
					<td>
						<Button variant="outline-secondary"
								onClick={() => this.props.showSplitTransactionModalFunc(transactionId, transactionCategoryId)}
						>
							Split
						</Button>
					</td>
				</tr>
			);
		});

		return (
			<div hidden={this.props.hidden.toString() === 'true'}>
				<span>
					<label for="fromDate"
					>
						From
					</label>
					<input type="date" 
						   id="fromDate"
						   onChange={(event) => this.setState({...this.state, startDate: event.target.value})}
				    >
				    </input>

					<label for="toDate" 
					       className="dates-item"
			        >
			        	To
			        </label>
					<input type="date" 
						   id="toDate"
						   onChange={(event) => this.setState({...this.state, endDate: event.target.value})}
				    >
				    </input>

					<Button variant="outline-primary"
					        className="dates-item"
							onClick={this.getTransactions}
					>
						Search
					</Button>
				</span>

				<Table striped bordered hover>
					<thead>
					    <tr>
					      <th hidden>ID</th>
					      <th>Date</th>
					      <th>Payee</th>
					      <th>Amount</th>
					      <th>Institution ID</th>
					      <th>Category</th>
					      <th>Check Num</th>
					      <th>Memo</th>
					      <th>Sic</th>
					      <th>Mcc</th>
					      <th>Type</th>
					      <th>Actions</th>
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