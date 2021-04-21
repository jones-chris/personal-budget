import React, { Component } from "react";
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import './Category.css';

class Category extends Component {

	constructor(props) {
		super(props);

		this.state = {
			initialized: false,
			categories: []
		}
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

	render() {
		if (!this.props.hidden) {
			if (!this.state.initialized) {
				this.getCategories();
				this.setState({...this.state, initialized: true});
			}
		}

		// Categories table rows JSX
		let categoriesJsx = []
		this.state.categories.forEach(category => {
			categoriesJsx.push(
				<tr key={category.id}>
					<td>{category.id}</td>
					<td>{category.name}</td>
					<td>
						<Button variant="secondary">Edit</Button>
						<Button variant="danger">Delete</Button>
					</td>
				</tr>
			)
		});

		return (
			<div hidden={this.props.hidden.toString() === 'true'}>
				<Button variant="primary" className="add-category-button">Add Category</Button>

				<Table striped bordered hover>
					<thead>
					    <tr>
					      <th>ID</th>
					      <th>Name</th>
					      <th>Actions</th>
					    </tr>
					  </thead>
					  <tbody>
					  	{categoriesJsx}
					  </tbody>
				</Table>
			</div>
		);
	}

}

export default Category;