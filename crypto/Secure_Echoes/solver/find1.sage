import hashlib, string, random

def generate_hashes(n):
    messages, hashes = [], []
    for _ in range(n):
        msg = ''.join(random.choices(string.ascii_letters + string.digits, k=29))
        h_int = int(hashlib.sha256(msg.encode()).hexdigest(), 16)
        messages.append(msg); hashes.append(h_int)
    return messages, hashes

def solve_range_sum(messages, hashes, mod_val, max_coeff=100):
    n = len(hashes)
    messages_int = [int.from_bytes(m.encode(), 'big') for m in messages]
    H = [(h + pow(m, 4, mod_val) + 3*pow(m, 3, mod_val) + 3*pow(m, 2, mod_val) + 7*m) % mod_val for m,h in zip(messages_int, hashes)]
    
    # Midpoint of our target range [0, max_coeff]
    mid = max_coeff / 2
    
    # K1: Penalty for the sum not being 0 mod 2^256
    # K2: Scaling factor for coefficients
    K1 = 2**600
    K2 = 1
    
    rows = []
    # 1. Modular Sum constraint rows
    for i in range(n):
        row = [0] * (n + 1)
        row[0] = int(H[i] * K1)
        row[i+1] = K2
        rows.append(row)
        
    # 2. Modulus wrap-around row
    rows.append([int(mod_val * K1)] + [0] * n)
    
    # 3. Target Embedding Row
    # We target the midpoint 'mid'. LLL will find values v_i 
    # such that (v_i + mid) is an integer near mid.
    target_row = [0] + [int(-mid * K2)] * n
    
    # Construct Matrix and add the embedding helper
    # We add a 1 at the end to keep the embedding row scaled
    M = Matrix(ZZ, rows)
    M = M.stack(vector(ZZ, target_row))
    
    # Add a column of zeros and a 1 at the bottom to stabilize the embedding
    M = M.augment(vector(ZZ, [0]*(n+1) + [1]))

    print(f"Reducing {M.nrows()}x{M.ncols()} lattice (N={n}, Range=[0, {max_coeff}])...")
    L = M.LLL()
    
    for row in L:
        # Check if the sum is 0 mod 2^256 (first column)
        # and if the embedding scale factor is +/- 1
        if row[0] == 0 and abs(row[-1]) == 1:
            flip = row[-1] # Adjust if LLL found the negative of our target
            coeffs = []
            valid = True
            
            for i in range(1, n + 1):
                # Reconstruct l_i: l_i = (v_i / K2) + mid
                l_i = (row[i] * flip / K2) + mid
                if l_i.is_integer() and 0 <= l_i <= max_coeff:
                    coeffs.append(int(l_i))
                else:
                    valid = False
                    break
            
            if valid and any(c > 0 for c in coeffs):
                return coeffs
    return None

# --- Runtime ---
MOD = 2**256
N = 40

messages, hashes = generate_hashes(N)
coeffs = solve_range_sum(messages, hashes, MOD)



if coeffs:
    print(coeffs)
    print(messages)
    print("\n--- Success! ---", sum(coeffs))
    # calc_sum = 0
    # used_count = 0
    # for i, l in enumerate(coeffs):
    #     if l > 0:
    #         calc_sum = (calc_sum + l * (hashes[i] + )) % MOD
    #         print(f"Coeff: {l:2} | Msg: '{messages[i]}'")
    #         used_count += 1
    
    # print(f"\nUsed {used_count} messages.")
    # print(f"Verification (Sum mod 2^256): {calc_sum}")
    # if calc_sum == 0:
    #     print("RESULT IS EXACTLY ZERO")
else:
    print("\nNo solution found in the positive range. Try increasing N slightly.")