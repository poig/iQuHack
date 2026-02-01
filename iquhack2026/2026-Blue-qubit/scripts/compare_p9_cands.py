def compare_solutions():
    s_my = "11010001100000100110001000001111110000001100001010010011"
    s_im = "00111101110101010011100001111011110111100000111101010111"
    s_zx = "00111001000111000010100000111010111110110101001100001100"
    
    # Calculate Hamming distances
    def hamming(s1, s2):
        return sum(c1 != c2 for c1, c2 in zip(s1, s2))
        
    print(f"My Result vs Improved: {hamming(s_my, s_im)}")
    print(f"My Result vs PyZX:     {hamming(s_my, s_zx)}")
    print(f"Improved vs PyZX:      {hamming(s_im, s_zx)}")
    
    # Check if they look inverted
    def inverse_hamming(s1, s2):
        s2_inv = "".join('1' if c=='0' else '0' for c in s2)
        return hamming(s1, s2_inv)
        
    print(f"My Result vs Inv(Improved): {inverse_hamming(s_my, s_im)}")

if __name__ == "__main__":
    compare_solutions()
