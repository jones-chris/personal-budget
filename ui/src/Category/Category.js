import React, { Component } from "react";
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import './Category.css';
import InputGroup from 'react-bootstrap/InputGroup';
import Form from 'react-bootstrap/Form'

class Category extends Component {

	constructor(props) {
		super(props);

		this.state = {
			initialized: false,
			categories: [],
			newCategoryName: null
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

	// TODO:  Add this function back when you add the ability to change a category name.
	// updateCategoryName = async (categoryId, categoryName) => {
	// 	const response = await fetch(
	// 		'http://localhost:5000/category',
	// 		{
	// 			method: 'POST',
	// 			headers: {
	// 				'Content-Type': 'application/json'
	// 			},
	// 			body: JSON.stringify({
	// 				id: categoryId,
	// 				name: categoryName
	// 			})
	// 		}
	// 	)

	// 	if (response.status === 200) {
	// 		this.getCategories();
	// 	} else {
	// 		let responseJson = response.json();
			
	// 		console.log(responseJson);

	// 		alert('There was an error updating the category');
	// 	}
	// }

	deleteCategory = async (categoryId) => {
		const response = await fetch(
			'http://localhost:5000/category',
			{
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					id: categoryId
				})
			}
		)

		if (response.status === 200) {
			this.getCategories();
		} else {
			let responseJson = response.json();
			
			console.log(responseJson);

			alert('There was an error deleting the category');
		}
	}

	createNewCategory = async () => {
		let newCategoryName = this.state.newCategoryName; 

		const response = await fetch(
			'http://localhost:5000/category',
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					id: null,
					name: newCategoryName
				})
			}
		)

		if (response.status === 201) {
			this.getCategories();
		} else {
			let responseJson = response.json();
			
			console.log(responseJson);

			alert('There was an error saving the category');
		}
	}

	onNewCategoryNameChange = (name) => {
		this.setState({...this.state, newCategoryName: name});
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
			const categoryId = category.id;

			categoriesJsx.push(
				<tr key={categoryId}>
					<td>{categoryId}</td>
					<td>{category.name}</td>
					<td>
					    {/*TODO:  Add this function back when you add the ability to change a category name.*/}
						{/*<Button variant="secondary"
								onClick{(event) => this.updateCategoryName(categoryId, event.target.value)}
						>
							Edit
						</Button>*/}
						<Button variant="danger"
						        onClick={() => this.deleteCategory(categoryId)}
						>
							Delete
						</Button>
					</td>
				</tr>
			)
		});

		return (
			<div hidden={this.props.hidden.toString() === 'true'}>
				<InputGroup className="add-category-div">
				    <Form.Control
				      placeholder="Category Name"
				      aria-label="Category Name"
				      aria-describedby="basic-addon2"
				      onChange={(event) => this.onNewCategoryNameChange(event.target.value)}
				    />
				    <InputGroup.Append>
      					<Button variant="outline-primary"
      					        onClick={this.createNewCategory}
      					>
      						Add Category
      					</Button>
  					</InputGroup.Append>
			    </InputGroup>
				

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