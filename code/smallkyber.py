from sympy import poly,div,Poly,simplify
from sympy.abc import x
from sympy.polys.specialpolys import random_poly
import random
import hashlib
import secrets

DEBUG = False

class SmallKyber:
    """
    le variabili che caratterizzano una implementazione di Small Kyber sono:
        - q         <=> il modulo dei coefficienti
        - n         <=> il grado del polinomio che funge da modulo
        - polymod   <=> il polinomio modulo
    """

    """
    l'inizializzazione deve prevedere il setup di q, n e polymod=x**n+1
    """
    def __init__(self,n=256,q=3329,k=2):
        self.q = q                                                                  # numerical modulus
        self.n = n                                                                  # polynomial modulus degree
        self.polymod = poly(x**n+1)                                                 # polynomial modulus
        self.k = k

    class Util:
        """
        questa classe contiene le funzioni che permettono di convertire polinomi, interi e array di byte tra di loro.
        """
        def polyToInt(p):
            i = 0
            for coeff in Poly(p).all_coeffs():
                i *= 2
                i += coeff
            return i
        def intToPoly(m):
            p = 0
            i = 0
            for cifra in reversed(str(bin(m))[2:]):
                p += int(cifra)*x**i
                i += 1
            return p
        def bytesToPoly(b):
            return SmallKyber.Util.intToPoly(int.from_bytes(b,'big'))
        def polyToBytes(p):
            integer =  abs(int(SmallKyber.Util.polyToInt(p)))
            return integer.to_bytes((integer.bit_length() + 7) // 8, 'big')

    class Keccak:
        """
        hash functions, useful for the KEM
        """
        def H(params):
            H_ = hashlib.new('sha3_256')
            H_.update(params)
            return H_.digest()
        def G(params):
            G_ = hashlib.new('sha3_512')
            G_.update(params)
            return G_.digest()


    """
    mediante questa funzione effettuo la moltiplicazione polinomiale modulare tra matrice e vettore
    """
    def multiply(self,A:[],s:[]):
        vect = []
        for i in range(self.k):
            coefficients = Poly(div((sum(s[j]*A[i][j] for j in range(self.k))),self.polymod)[1]).all_coeffs()
            mod_coeff = [coeff % self.q for coeff in coefficients]
            vect.append(Poly(sum(coeff*x**i for i, coeff in enumerate(reversed(mod_coeff)))))
        return vect

    def isNear(self,value):
        value = (value+self.q)%self.q
        if float(value/self.q)>0.25 and float(value/self.q)<0.75:
            return 1
        return 0

    """
    mediante questa funzione genero una coppia di chiavi (privata,pubblica)
    """
    def CPA_KeyGen(self):
        """
        CPA_KeyGen() -> s,[t,rho]
        """
        try:
            # \rho,\sigma \leftarrow \{0,1\}^{256}
            rho,sigma = [secrets.randbelow(2**256),secrets.randbelow(2**256)]
            # A \sim R_q^{k\times k} := Sam(\rho)
            random.seed(rho)
            A = [ [ sum((random.randint(0,self.q-1))*x**i for i in range(self.n) ) for _ in range(self.k) ] for _ in range(self.k) ]
            # (s,e) \sim \beta_\eta^k\times\beta_\eta^k := Sam(\sigma)
            random.seed(sigma)
            s = [ sum((random.randint(-1,1)%self.q)*x**i for i in range(self.n)) for _ in range(self.k) ]
            e = [ sum((random.randint(-1,1)%self.q)*x**i for i in range(self.n)) for _ in range(self.k) ]
            # t = Compress_q(As+e,d_t) => baby version: t = As + e
            product = self.multiply(A,s)
            t = []
            for j in range(self.k):
                t.append(
                    sum(
                        coeff*x**i
                        for i,coeff
                        in enumerate(
                            reversed(
                                [
                                    coef % self.q
                                    for coef
                                    in (product[j]+e[j]).all_coeffs()
                                    ]
                                )
                            )
                    )
                )
            return ((t,rho),s)
        except Exception as e:
            print(e)
            return  self.CPA_KeyGen()

    """
    mediante questa funzione encrypto un messaggio che mi arriva come intero positivo
    """
    def CPA_Enc(self,t,rho,message:int,rgen=None):
        if message < 0 or message >= 2**256:
            return -1, "this message is too long for these parameters or the message is negative"
        # r \leftarrow \{0,1\}^{256}
        if rgen == None:
            rgen = secrets.randbelow(2**256)
        # t := Decompress_q(t,d_t) isn't necessary in this implementation
        # A \sim R_q^{k\times k} := Sam(\rho)
        random.seed(rho)
        A = [ [ sum((random.randint(0,self.q-1))*x**i for i in range(self.n) ) for _ in range(self.k) ] for _ in range(self.k) ]
        # (r,e_1,e_2) \sim \beta_\eta^k\times\beta_\eta^k\times\beta_\eta := Sam(r)
        random.seed(rgen)
        r = [ sum((random.randint(-1,1)%self.q)*x**i for i in range(self.n)) for _ in range(self.k)]
        e_1 = [ sum((random.randint(-1,1)%self.q)*x**i for i in range(self.n)) for _ in range(self.k)]
        e_2 = sum((random.randint(-1,1)%self.q)*x**i for i in range(self.n))
        # m must be \in \mathcal{M}
        message_poly = SmallKyber.Util.intToPoly(message)
        # u = Compress_q(A^Tr+e_1,d_u)
        u = []
        A_transposed = [[A[j][i] for j in range(self.k)] for i in range(self.k)]
        product = self.multiply(A_transposed,r)
        for j in range(self.k):
            u.append(
                sum(
                    coeff*x**i
                    for i, coeff
                    in enumerate(
                        reversed(
                            [
                                coef % self.q
                                for coef
                                in (
                                    (product[j]+e_1[j]).all_coeffs()
                                )
                            ]
                        )
                    )
                )        
            )
        # v = Compress_q(t^Tr+e_2+\lceil \frac{q}{2} \rfloor\cdot m,d_v)
        v = sum(
                coeff*x**i
                for i, coeff
                in enumerate(
                    reversed(
                        [
                            coef % self.q
                            for coef
                            in (div(sum(t[j]*r[j] for j in range(self.k)),self.polymod)[1]+e_2+(self.q//2+self.q%2)*message_poly).all_coeffs()
                        ]
                    )
                )
            )
        return u,v

    """
    la presente decifra avendo u,v e il sistema inizializzato con i giusti parametri
    """
    def CPA_Dec(self,s,u,v):
        # v - s^Tu
        noisy_m_n = v - sum(
            coeff*x**i
            for i, coeff
            in enumerate(
                reversed(
                    [
                        coef % self.q
                        for coef
                        in (div(sum(s[j]*u[j] for j in range(self.k)),self.polymod)[1]).all_coeffs()
                    ]
                )
            )
        )
        m = 0
        for coef in Poly(noisy_m_n).all_coeffs():
            m *= 2
            m += self.isNear(coef)
        return m

    """
    Questa funzione esegue l'incapsulamento
    """
    def Encaps(self,t,rho):
        # m \leftarrow \{0,1\}^{256}
        m = secrets.randbelow(2**256)
        # (K_hat,r) := G(H(pk),m)
        a = b''                                                                 # come prima cosa ricavo pk in forma più gestibile
        for i in t:
            a += SmallKyber.Util.polyToBytes(i)
        hash = SmallKyber.Keccak.G(SmallKyber.Keccak.H(a)+m.to_bytes(32,'big'))   # effettuo l'hash
        K_hat,r = [hash[:32],int.from_bytes(hash[32:],'big')]                         # blocchi da 32 byte
        # (u,v) := Kyber.CPA.Enc((t,rho),m;r)
        u,v = self.CPA_Enc(t,rho,m,rgen=r)
        # c = (u,v) ossia traduco u,v in un unico array di byte così mi diventa gestibile il tutto
        a = b''
        for element in u:
            a += SmallKyber.Util.polyToBytes(element)
        # K := H(K_hat,H(c))
        K = SmallKyber.Keccak.H(K_hat+SmallKyber.Keccak.H(a+SmallKyber.Util.polyToBytes(v)))
        return (u,v,int.from_bytes(K,'big'))

    """
    Questa funzione esegue il decapsulamento
    """

    def Decaps(self,s,z,t,rho,u,v):
        # m' := Kyber.CPA.Dec(s,(u,v))
        m_prime = self.CPA_Dec(s,u,v)
        # (K_hat_prime,r_prime) := G(H(pk),m_prime)
        a = b''                                                                 # ricavo pk in forma gestibile
        for i in t:
            a += SmallKyber.Util.polyToBytes(i)
        hash = SmallKyber.Keccak.G(SmallKyber.Keccak.H(a)+m_prime.to_bytes(32,'big'))
        [K_hat_prime,r_prime] = [hash[:32], int.from_bytes(hash[32:],'big')]
        # (u',v') := Kyber.CPA.Enc((t,rho),m';r')
        u_prime,v_prime = self.CPA_Enc(t,rho,m_prime,rgen=r_prime)
        # confronti
        if u_prime == u and v_prime == v:
            a = b''
            for element in u_prime:
                a += SmallKyber.Util.polyToBytes(element)
            K = SmallKyber.Keccak.H(K_hat_prime+SmallKyber.Keccak.H(a+SmallKyber.Util.polyToBytes(v_prime)))
            return int.from_bytes(K,'big')
        else:
            tmp = b''
            for element in u_prime:
                tmp += SmallKyber.Util.polyToBytes(element)
            K = SmallKyber.Keccak.H(z.to_bytes(32,'big')+SmallKyber.Keccak.H(tmp+SmallKyber.Util.polyToBytes(v_prime)))
            return int.from_bytes(K,'big') 


if __name__ == "__main__":

################# TESTS #################

    print("instantiating...")
    bk = SmallKyber(256,3329,4)
    print("instantiation successful...")

    # testing the IND-CPA Encryption Mechanism
    """"for _ in range(100):
        print("----------\ngenerating keys...")
        [t,rho],s = bk.CPA_KeyGen()
        print("key generation successful...")
        print("generating message...")
        m = secrets.randbelow(2**256)
        print("generating ciphertext...")
        u,v = bk.CPA_Enc(t,rho,m,rgen=secrets.randbelow(2**256))
        print("generating plaintext...")
        m_prime = bk.CPA_Dec(s,u,v)
        print("testing outputs")
        print(m==m_prime,m,m_prime)"""
    
    # testing the KEM
    """for _ in range(100):
        print("----------\ngenerating keys...")
        [t,rho],s = bk.CPA_KeyGen()
        print("key generation successful...")
        u,v,K = bk.Encaps(t,rho)
        print("encapsulation succeded...")
        K_prime = bk.Decaps(s,secrets.randbelow(2**256),t,rho,u,v)
        print("decapsulation succeded...")
        print("testing outputs...")
        print(K==K_prime,K, K_prime)"""
        
    [t,rho],s = bk.CPA_KeyGen()
    u,v,K = bk.Encaps(t,rho)
    K_prime = bk.Decaps(s,secrets.randbelow(2**256),t,rho,u,v)
    print(K==K_prime,K, K_prime)



"""
    PROTOTIPI:
    NEW
    SmallKyber(n,q,k)
    SmallKyber(n,q,k).CPA_KeyGen() -> (t,rho),s
    SmallKyber(n,q,k).CPA_Enc((t,rho),m) -> (u,v)
    SmallKyber(n,q,k).Encaps(t,rho) -> (u,v,K)
    SmallKyber(n,q,k).Decaps(s,z,t,rho,u,v) -> K
"""
