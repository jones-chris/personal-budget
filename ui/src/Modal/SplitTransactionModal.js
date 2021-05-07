import React, { Component } from 'react';
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import Table from 'react-bootstrap/Table';

class SplitTransactionModal extends Component {

	constructor(props) {
		super(props);

		this.state = {
			initialized: false,
			transactionId: null,
			transactionCategoryId: null,
			transactionCategories: [
				{
					id: 0,
					categoryId: null,
					amount: null
				}
			],
			categories: []
		};
	}

	getCategories = () => {
		fetch(
            'http://localhost:5000/categories'
		).then(response => response.json())
		 .then(responseJson => {
			let newState = {...this.state};
			newState.categories = responseJson;
			newState.transactionId = this.props.transactionId;
			newState.transactionCategoryId = this.props.transactionCategoryId;
			this.setState(newState);
		 })
	}

	onAddTransactionCategory = () => {
		let newState = {...this.state};
		newState.transactionCategories.push({
			id: this.state.transactionCategories.length,
			categoryId: null,
			amount: null
		})
		this.setState(newState);
	}

	onDeleteTransactionCategory = (id) => {
		let newState = {...this.state};

		let newTransactionCategories = newState.transactionCategories.filter(transactionCategory => transactionCategory.id !== id);
		
		// Renumber the transaction category IDs.
		newTransactionCategories.forEach((transactionCategory, index) => {
			transactionCategory.id = index;
		});

		newState.transactionCategories = newTransactionCategories;

		this.setState(newState);
	}

	onUpdateAmount = (id, amount) => {
		let newState = {...this.state};

		let transactionCategoryToUpdate = newState.transactionCategories.filter(transactionCategory => transactionCategory.id === id)[0];
		transactionCategoryToUpdate.amount = amount;

		this.setState(newState);
	}

	onUpdateCategory = (id, categoryId) => {
		if (categoryId === '') {
			return;
		}

		let newState = {...this.state};
		
		let transactionCategoryToUpdate = newState.transactionCategories.filter(transactionCategory => transactionCategory.id === id)[0];
		transactionCategoryToUpdate.categoryId = parseInt(categoryId);

		this.setState(newState);
	}

	onSave = async () => {
		// First check that all transaction categories do not have nulls, undefined, or empty strings as values.
		this.state.transactionCategories.forEach(transactionCategory => {
			if (transactionCategory.categoryId === undefined || transactionCategory.categoryId === null || transactionCategory.categoryId === '') {
				alert('A transaction category\'s category is undefined, null, or an empty string.  Please correct this before saving.');
				return;
			}

			if (transactionCategory.amount === undefined || transactionCategory.amount === null || transactionCategory.amount === '') {
				alert('A transaction category\'s amount is undefined, null, or an empty string.  Please correct this before saving.');
				return;
			}
		});

		// Transform the transction categories into the API's expected format.
		let requestTransactionCategories = this.state.transactionCategories.map(transactionCategory => {
			return {
				id: this.state.transactionCategoryId,
				category_id: transactionCategory.categoryId,
				transaction_id: this.state.transactionId,
				amount: parseFloat(transactionCategory.amount)
			}
		});

		// Save all transaction categories.
		let httpMethod;
		let uri;
		if (this.state.transactionId && ! this.state.transactionCategoryId) {
			httpMethod = 'POST';
			uri = 'http://localhost:5000/transaction/category';
		} else {
			httpMethod = 'PUT';
			uri = `http://localhost:5000/transaction/category/${this.state.transactionCategoryId}`;
		}

		const response = await fetch(
			uri,
			{
				method: httpMethod,
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(requestTransactionCategories)
			}
		)

		if (response.status === 200) {
			this.props.onCloseHandler();
		} else {
			let responseJson = await response.json();
			console.log(responseJson);

			let message = responseJson.message;
			alert(message);
		}
	}

	render() {
		if (! this.props.hidden) {
			if (! this.state.initialized) {
				this.getCategories();
				let newState = {...this.state, initialized: true}
				this.setState(newState);
			}
		}

		// Create transaction category JSX.
		let transactionCategoriesJsx = [];
		this.state.transactionCategories.forEach(transactionCategory => {

			// Create categories JSX.
			let categoriesJsx = [];

			// Creat the default blank option.
			categoriesJsx.push(
				<option value=""></option>
			);

			this.state.categories.forEach(category => {
				categoriesJsx.push(
					<option value={category.id} selected={transactionCategory.categoryId === category.id}>{category.name}</option>
				)
			});

			let transactionCategoryId = transactionCategory.id;
			transactionCategoriesJsx.push(
				<tr>
					<td>
						<select onChange={(event) => this.onUpdateCategory(transactionCategoryId, event.target.value)}>
							{categoriesJsx}
						</select>
					</td>
					<td>
						<input value={transactionCategory.amount}
							   onChange={(event) => this.onUpdateAmount(transactionCategoryId, event.target.value)}
						></input>
					</td>
					<td>
						<Button variant="outline-danger"
							    onClick={() => this.onDeleteTransactionCategory(transactionCategoryId)}
						>
							Delete
						</Button>
					</td>
				</tr>
			);
		});

		return (
			<Modal show={! this.props.hidden} backdrop='static' size="lg" onHide={this.props.onCloseModalHandler}>
				<Modal.Header closeButton>
			        <Modal.Title>Split Transaction Categories</Modal.Title>
			    </Modal.Header>

			    <Modal.Body>
			    	<Button variant="outline-primary"
			    			onClick={this.onAddTransactionCategory}
			    	>
			    		+
		    		</Button>

			    	<Table striped bordered hover>
			    		<thead>
			    			<tr>
			    				<th>Category</th>
			    				<th>Amount</th>
			    				<th>Actions</th>
			    			</tr>
			    		</thead>
			    		<tbody>
			    			{transactionCategoriesJsx}
			    		</tbody>
			    	</Table>
			    </Modal.Body>

			    <Modal.Footer>
			    	<Button variant="outline-secondary" onClick={this.props.onCloseModalHandler}>
			        	Close
			        </Button>
			        <Button variant="outline-primary" onClick={this.onSave}>
			            Save
			        </Button>
			    </Modal.Footer>
			</Modal>
		);
	}

}

export default SplitTransactionModal;