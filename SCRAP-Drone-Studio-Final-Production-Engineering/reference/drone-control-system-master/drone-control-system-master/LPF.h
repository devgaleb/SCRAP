class LPF {
    public:
    float y,fc,Ts,alpha;

    LPF();
    float Output(float x, float Ts);
    void change_parameters(float fc, float initial_y);
};