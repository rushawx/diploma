"""
Custom ALS implementation
"""
import numpy as np
from sklearn.metrics import mean_squared_error


class ExplicitALS:
    """
    ALS implementation optimized for explicit ratings with anti-overfitting measures
    """

    def __init__(self, n_factors=15, n_iterations=20, early_stopping_rounds=3,
                 user_reg=1.0, item_reg=1.0, random_state=42):
        self.n_factors = n_factors
        self.n_iterations = n_iterations
        self.user_reg = user_reg
        self.item_reg = item_reg
        self.early_stopping_rounds = early_stopping_rounds
        self.random_state = random_state
        self.user_factors = None
        self.item_factors = None
        self.training_history = []

    def fit(self, rating_matrix, validation_matrix=None):
        """
        Train ALS model on explicit rating matrix with early stopping
        """
        np.random.seed(self.random_state)
        n_users, n_items = rating_matrix.shape

        # Initialize factors with smaller values to reduce overfitting
        self.user_factors = np.random.normal(0, 0.05, (n_users, self.n_factors))
        self.item_factors = np.random.normal(0, 0.05, (n_items, self.n_factors))

        rows, cols = rating_matrix.nonzero()

        user_items = {u: [] for u in range(n_users)}
        item_users = {i: [] for i in range(n_items)}

        for u, i in zip(rows, cols):
            rating = rating_matrix[u, i]
            user_items[u].append((i, rating))
            item_users[i].append((u, rating))

        best_validation_error = float('inf')
        patience_counter = 0
        best_user_factors = None
        best_item_factors = None

        for iteration in range(self.n_iterations):
            # Update user factors with user-specific regularization
            for u in range(n_users):
                if len(user_items[u]) > 0:
                    items_u = [i for i, _ in user_items[u]]
                    ratings_u = np.array([r for _, r in user_items[u]], dtype=float)

                    item_factors_u = self.item_factors[items_u]

                    # Use user_reg for user factors to reduce overfitting
                    A = item_factors_u.T @ item_factors_u + self.user_reg * np.eye(self.n_factors)
                    b = item_factors_u.T @ ratings_u

                    self.user_factors[u] = np.linalg.solve(A, b)

            # Update item factors with item-specific regularization
            for i in range(n_items):
                if len(item_users[i]) > 0:
                    users_i = [u for u, _ in item_users[i]]
                    ratings_i = np.array([r for _, r in item_users[i]], dtype=float)

                    user_factors_i = self.user_factors[users_i]

                    # Use item_reg for item factors to reduce overfitting
                    A = user_factors_i.T @ user_factors_i + self.item_reg * np.eye(self.n_factors)
                    b = user_factors_i.T @ ratings_i

                    self.item_factors[i] = np.linalg.solve(A, b)

            # Calculate training error
            train_pred = self.predict(rating_matrix)
            train_mse = self._calculate_mse(rating_matrix, train_pred)

            # Early stopping with validation data
            if validation_matrix is not None:
                val_pred = self.predict(validation_matrix)
                val_mse = self._calculate_mse(validation_matrix, val_pred)

                # Track training history
                self.training_history.append({
                    'iteration': iteration,
                    'train_mse': train_mse,
                    'val_mse': val_mse
                })

                # Check for improvement
                if val_mse < best_validation_error:
                    best_validation_error = val_mse
                    patience_counter = 0
                    # Save best factors
                    best_user_factors = self.user_factors.copy()
                    best_item_factors = self.item_factors.copy()
                else:
                    patience_counter += 1

                if iteration % 2 == 0 or iteration == self.n_iterations - 1:
                    print(f"Iteration {iteration}, Train MSE: {train_mse:.4f}, Val MSE: {val_mse:.4f}")

                # Early stopping
                if patience_counter >= self.early_stopping_rounds:
                    print(f"Early stopping at iteration {iteration}")
                    self.user_factors = best_user_factors
                    self.item_factors = best_item_factors
                    break
            else:
                # No validation data, just track training
                self.training_history.append({
                    'iteration': iteration,
                    'train_mse': train_mse
                })

                if iteration % 5 == 0 or iteration == self.n_iterations - 1:
                    print(f"Iteration {iteration}, Train MSE: {train_mse:.4f}")

        print(f"Training completed after {iteration + 1} iterations")

    def predict(self, rating_matrix):
        """
        Predict ratings for all user-item pairs in the matrix
        """
        rows, cols = rating_matrix.nonzero()
        predictions = np.zeros(len(rows))

        for idx, (u, i) in enumerate(zip(rows, cols)):
            predictions[idx] = self.user_factors[u] @ self.item_factors[i]

        return predictions

    def predict_all(self):
        """
        Predict ratings for all user-item pairs
        """
        return self.user_factors @ self.item_factors.T

    def recommend(self, user_idx, n_recommendations=10, exclude_seen=True):
        """
        Get top N recommendations for a user
        """
        user_vector = self.user_factors[user_idx]
        scores = user_vector @ self.item_factors.T

        if exclude_seen and hasattr(self, 'seen_items'):
            seen_items = self.seen_items[user_idx]
            for item in seen_items:
                scores[item] = -np.inf

        top_indices = np.argsort(-scores)[:n_recommendations]
        top_scores = scores[top_indices]

        return list(zip(top_indices, top_scores))

    def _calculate_mse(self, rating_matrix, predictions):
        """
        Calculate mean squared error
        """
        actual = rating_matrix.data
        return mean_squared_error(actual, predictions)


if __name__ == "__main__":
    print("Explicit ALS implementation ready!")
    print("This implementation correctly handles:")
    print("- Explicit ratings (1-5 scale)")
    print("- Proper factor learning")
    print("- Non-zero item factors")
