package codes.dbg;

import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;

import java.util.Random;

@State(Scope.Benchmark)
public class FindMaxBenchmark {
    public static int SIZE = 1_000_000;

    @Benchmark
    @CompilerControl(CompilerControl.Mode.DONT_INLINE)
    public static void findMax_if(Blackhole bh, Mock mock) {
        int result = Integer.MIN_VALUE;
        int[] data = mock.tab;

        for (int i = 0; i < data.length; i++) {
            if (data[i] > result) {
                result = data[i];
            }
        }

        bh.consume(result);
    }

    @Benchmark
    @CompilerControl(CompilerControl.Mode.DONT_INLINE)
    public static void findMax_if_else(Blackhole bh, Mock mock) {
        int result = Integer.MIN_VALUE;
        int[] data = mock.tab;

        for (int i = 0; i < data.length; i++) {
            if (data[i] > result) {
                result = data[i];
            } else {
                result = result;
            }
        }

        bh.consume(result);
    }

    @Benchmark
    @CompilerControl(CompilerControl.Mode.DONT_INLINE)
    public static void findMax_ternary(Blackhole bh, Mock mock) {
        int result = Integer.MIN_VALUE;
        int[] data = mock.tab;

        for (int i = 0; i < data.length; i++) {
            result = data[i] > result ? data[i] : result;
        }

        bh.consume(result);
    }

    @Benchmark
    @CompilerControl(CompilerControl.Mode.DONT_INLINE)
    public static void findMax_intrinsicMax(Blackhole bh, Mock mock) {
        int result = Integer.MIN_VALUE;
        int[] data = mock.tab;

        for (int i = 0; i < data.length; i++) {
            result = Math.max(data[i], result);
        }

        bh.consume(result);
    }

    @State(Scope.Thread)
    public static class Mock {
        private int[] tab = new int[SIZE];

        public int[] getTab() {
            return tab;
        }

        @Setup(Level.Iteration)
        public void setup() {
            Random r = new Random();
            this.tab = r.ints(SIZE).toArray();
        }
    }
}
