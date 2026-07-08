from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from models import Asset_Category
from forms import CategoryForm
from routes.helpers import admin_required

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')


@categories_bp.route('')
@login_required
def category_list():
    categories = Asset_Category.query.order_by(Asset_Category.name).all()
    return render_template('categories/list.html', categories=categories)


@categories_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def category_create():
    form = CategoryForm()

    if form.validate_on_submit():
        category = Asset_Category(
            name=form.name.data,
            description=form.description.data
        )

        db.session.add(category)
        db.session.commit()

        flash(f'Category {category.name} created successfully!', 'success')
        return redirect(url_for('categories.category_list'))

    return render_template('categories/create.html', form=form)


@categories_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def category_edit(id):
    category = Asset_Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    form.original_name = category.name

    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data

        db.session.commit()
        flash(f'Category {category.name} updated successfully!', 'success')
        return redirect(url_for('categories.category_list'))

    return render_template('categories/edit.html', form=form, category=category)


@categories_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def category_delete(id):
    category = Asset_Category.query.get_or_404(id)

    if category.assets:
        flash(f'Cannot delete "{category.name}" — it still has {len(category.assets)} asset(s) assigned.', 'error')
        return redirect(url_for('categories.category_list'))

    name = category.name
    db.session.delete(category)
    db.session.commit()

    flash(f'Category {name} deleted successfully!', 'success')
    return redirect(url_for('categories.category_list'))
