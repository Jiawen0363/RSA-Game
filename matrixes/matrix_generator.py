import itertools
import json
import time


class MatrixGenerator:
    def __init__(self, shape):
        self.shape = shape
        self.all_matrices = []

    def is_canonical_with_fixed_first_row(self, matrix):
        """
        Check if the matrix is in canonical form with the first row fixed as [1,1,1]:
        1. The first row must be [1,1,1]
        2. The other rows are sorted lexicographically
        3. The column arrangement is lexicographically minimal
        """
        rows, cols = len(matrix), len(matrix[0])

        # Check if the first row is [1,1,1]
        first_row = tuple([1] * cols)
        if matrix[0] != first_row:
            return False

        # Check if the other rows are sorted
        for i in range(2, rows):
            if matrix[i] < matrix[i - 1]:
                return False

        # Check if the column arrangement is minimal
        cols_list = list(zip(*matrix))
        for perm in itertools.permutations(cols):
            perm_cols = [cols_list[i] for i in perm]
            perm_matrix = list(zip(*perm_cols))
            perm_matrix_sorted = [first_row] + sorted(
                perm_matrix[1:]
            )  # Keep the first row unchanged

            # If a smaller arrangement is found, it's not canonical
            if perm_matrix_sorted < matrix:
                return False

        return True

    def generate_canonical_with_fixed_first_row(self):
        """
        Generate only canonical matrices with the first row fixed as [1,1,1]
        """
        rows, cols = self.shape
        print(
            f"Generating canonical {rows}x{cols} matrices (first row fixed as [1,1,1])..."
        )

        # The first row is all 1s
        first_row = tuple([1] * cols)

        # Generate all possible rows (except all 1s)
        all_rows = []
        for combo in itertools.product([0, 1], repeat=cols):
            row = tuple(combo)
            if row != first_row:
                all_rows.append(row)

        print(f"Number of available rows: {len(all_rows)}")

        # Only generate canonical matrices
        canonical_matrices = []
        total_checked = 0

        # Generate all possible row combinations
        for row_combination in itertools.combinations(all_rows, rows - 1):
            total_checked += 1
            if total_checked % 10000 == 0:
                print(f"Checked {total_checked} combinations...")

            # Construct the matrix (first row + other rows)
            matrix = [first_row] + list(row_combination)

            # Sort the other rows (keep the first row unchanged)
            other_rows = sorted(matrix[1:])
            matrix_sorted = [first_row] + other_rows

            # Check if it is canonical
            if self.is_canonical_with_fixed_first_row(matrix_sorted):
                canonical_matrices.append(matrix_sorted)
                if len(canonical_matrices) <= 5:  # Only print the first 5
                    print(
                        f"Found canonical matrix {len(canonical_matrices)}: {matrix_sorted}"
                    )

        print(f"Total combinations checked: {total_checked}")
        print(f"Number of canonical matrices: {len(canonical_matrices)}")

        self.all_matrices = canonical_matrices
        return canonical_matrices

    def generate_canonical_fast_fixed_first_row(self):
        """
        Optimized version for fast generation of canonical matrices, with the first row fixed as [1,1,1]
        """
        rows, cols = self.shape
        print(
            f"Fast generation of canonical {rows}x{cols} matrices (first row fixed as [1,1,1])..."
        )

        # The first row is all 1s
        first_row = tuple([1] * cols)

        # Generate all possible rows (except all 1s)
        all_rows = []
        for combo in itertools.product([0, 1], repeat=cols):
            row = tuple(combo)
            if row != first_row:
                all_rows.append(row)

        print(f"Number of available rows: {len(all_rows)}")

        # Use a more efficient canonical form check
        canonical_matrices = []
        total_checked = 0

        for row_combination in itertools.combinations(all_rows, rows - 1):
            total_checked += 1
            if total_checked % 10000 == 0:
                print(f"Checked {total_checked} combinations...")

            # Construct the matrix and sort the other rows
            matrix = [first_row] + list(row_combination)
            other_rows = sorted(matrix[1:])
            matrix_sorted = [first_row] + other_rows

            # Fast check for canonical form
            if self.is_canonical_fast_fixed_first_row(matrix_sorted):
                canonical_matrices.append(matrix_sorted)
                if len(canonical_matrices) <= 5:
                    print(f"Found canonical matrix {len(canonical_matrices)}")

        print(f"Total combinations checked: {total_checked}")
        print(f"Number of canonical matrices: {len(canonical_matrices)}")

        self.all_matrices = canonical_matrices
        return canonical_matrices

    def is_canonical_fast_fixed_first_row(self, matrix):
        """
        Fast check for canonical form (optimized version), strictly following the original algorithm logic
        """
        rows, cols = len(matrix), len(matrix[0])
        first_row = tuple([1] * cols)

        # Check if the first row is [1,1,1]
        if matrix[0] != first_row:
            return False

        # Check if the other rows are sorted
        for i in range(2, rows):
            if matrix[i] < matrix[i - 1]:
                return False

        # According to the original algorithm: permute all columns, then sort rows
        cols_list = list(zip(*matrix))

        # Check if there is a smaller column arrangement
        for perm in itertools.permutations(range(cols)):
            if perm == tuple(range(cols)):  # Skip the original arrangement
                continue

            perm_cols = [cols_list[i] for i in perm]
            perm_matrix = list(zip(*perm_cols))
            # Key: sort all rows, including the first row!
            perm_matrix_sorted = tuple(sorted(perm_matrix))

            if perm_matrix_sorted < tuple(sorted(matrix)):
                return False

        return True

    def save_matrices_to_json(self, filename):
        """Save matrices to a JSON file"""
        matrices_dict = {}
        for i, matrix in enumerate(self.all_matrices, 1):
            matrices_dict[f"matrix{i}"] = matrix

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(matrices_dict, f, indent=2, ensure_ascii=False)

        print(f"Matrices saved to: {filename}")
        print(f"Total number of canonical matrices generated: {len(self.all_matrices)}")


if __name__ == "__main__":
    # Test 5x3 matrix
    test_shapes = (8, 5)
    print(f"Start generating canonical {test_shapes[0]}x{test_shapes[1]} matrices...")

    start_time = time.time()
    generator = MatrixGenerator(test_shapes)

    # Use the fast version, with the first row fixed
    matrices = generator.generate_canonical_fast_fixed_first_row()

    elapsed = time.time() - start_time
    print(f"Total time: {elapsed:.2f} seconds")

    # Save the results
    basepath = "$HOME/datasets/rsagame/01_matrixes/matrixes_unsorted"
    generator.save_matrices_to_json(
        basepath + f"/matrixes_{test_shapes[0]}x{test_shapes[1]}.json"
    )
