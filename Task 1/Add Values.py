#import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute
from qiskit import BasicAer
backend = BasicAer.get_backend('qasm_simulator')


#Majority Circuit
maj_c = QuantumCircuit(3, name='MAJ')
maj_c.cx(2, 1)
maj_c.cx(2, 0)
maj_c.ccx(0, 1, 2)
maj = maj_c.to_gate(label='MAJ')


#UnMajority Circuit
uma3_c = QuantumCircuit(3, name='UMA3')
uma3_c.x(1)
uma3_c.cx(0, 1)
uma3_c.toffoli(0, 1, 2)
uma3_c.x(1)
uma3_c.cx(2, 0)
uma3_c.cx(2, 1)
uma3 = uma3_c.to_gate(label='UMA3')


def cuccaro_adder(c:QuantumCircuit, cin:QuantumRegister, a:QuantumRegister, b:QuantumRegister, cout:QuantumRegister, uma=uma3):
    c.append(maj, [cin, b[0], a[0]])
    for i in range(1, len(b)):
        c.append(maj, [a[i-1], b[i], a[i]])

    c.cx(a[-1], cout)

    for i in reversed(range(1, len(b))):
        c.append(uma, [a[i-1], b[i], a[i]])
    c.append(uma, [cin, b[0], a[0]])

def generate_adder_circuit(n:int, uma=uma3):
    if n % 2 != 0:
        raise ValueError('Odd number of qubits')

    cin = QuantumRegister(1, 'c_in')
    a = QuantumRegister(n//2-1, 'a')
    b = QuantumRegister(n//2-1, 'b->s')
    cout = QuantumRegister(1, 'c_out')
    c = QuantumCircuit(cin, b, a, cout)
        
    cuccaro_adder(c, cin, a, b, cout, uma=uma)
    return c

#Adding two numbers
def add_two_numbers(bits:int,num1:list,num2:list,carry=0):
    n=(bits*2)+2
    cuccaro_n = generate_adder_circuit(n)
    cin = QuantumRegister(1, 'c_in')
    a = QuantumRegister(n//2-1, 'a')
    b = QuantumRegister(n//2-1, 'b->s')
    cout = QuantumRegister(1, 'c_out')
    creg = ClassicalRegister(n//2, 'sum')
    c = QuantumCircuit(cin, b, a, cout, creg)

    if carry == 1:
        c.x(cin[0])
    
    for i in range(len(num1)):
        if num1[i] == '1':
            c.x(a[len(num1)-1-i])
            
    for i in range(len(num2)):
        if num2[i] == '1':
            c.x(b[len(num2)-1-i])
    
    c.append(cuccaro_n.to_gate(label='CUCC'), [*cin, *b, *a, *cout])
    c.barrier()
    c.measure([*b, *cout], creg)

    return (execute(c, backend, shots=128).result().get_counts(c))

#Creates all subsets
def powerset(lst:list):
    ans=[]
    for i in range(1,1 << len(lst)):
        ans.append([lst[j] for j in range(len(lst)) if (i & (1 << j))])
    return ans

#Adds n numbers
def add_n_numbers(i:list,n:int,m:int):
    if len(i) > 1:
        ans=i[0][n:m]
        for j in range(1,len(i)):
            num1=ans
            num2=i[j][n:m].zfill(len(ans))
            result = add_two_numbers(len(ans),num1,num2,carry=0)
            ans = max(result, key=result.get)
        return ans

def main(lst:list,value:int):
    QRAM=[]
    max_len = len(bin(max(lst))[2:])
    for i in range(0,len(lst)):
        QRAM.append( bin(1 << i)[2:].zfill(len(lst))[::-1] + bin(lst[i])[2:].zfill(max_len) )
    print("QRAM:",QRAM)
    print("\nResults: ")
    for i in powerset(QRAM):
        ans="0"
        if len(i)==1:
            ans = ans+i[0][-max_len:]
        elif len(i) > 1:
            ans = add_n_numbers(i,-max_len,len(i[0]))
        if ans == bin(value)[2:].zfill(len(ans)):
            ints = []
            for ii in i:
                ints.append(int(ii[-max_len:],2))
            print(ints,"==> ",end="")
            if len(i) > 1:
                ans_d=add_n_numbers(i,0,-max_len)[-len(lst):]
                print("|"+ans_d+">")
            elif len(i)==1:
                print("|"+i[0][0:-max_len]+">")
    

if __name__=="__main__":
    lst = [5, 7, 9, 8, 1]
    value = 16
    print("Given list:",lst)
    main(lst,value)
