import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { useWebSocket } from '../../hooks/useWebSocket';
import { WS_URL } from '../../constants/config';

export const PROGRAM_LIST = [
  { id: 1, title: '1. Hello World & Basic I/O', defaultInputs: { name: 'Sarah', age: 28 } },
  { id: 2, title: '2. Arithmetic Calculator', defaultInputs: { num1: 15, num2: 3, operation: 'multiply' } },
  { id: 3, title: '3. Odd or Even Checker', defaultInputs: { n: 17 } },
  { id: 4, title: '4. Area & Circumference of Circle', defaultInputs: { radius: 7 } },
  { id: 5, title: '5. Swap Two Variables', defaultInputs: { a: 'Value A', b: 'Value B' } },
  { id: 6, title: '6. Maximum of Three Numbers', defaultInputs: { a: 45, b: 89, c: 23 } },
  { id: 7, title: '7. Leap Year Identifier', defaultInputs: { year: 2024 } },
  { id: 8, title: '8. Celsius to Fahrenheit', defaultInputs: { temp: 37, mode: 'c_to_f' } },
  { id: 9, title: '9. Simple Interest Calculator', defaultInputs: { principal: 5000, rate: 6.5, time: 3 } },
  { id: 10, title: '10. Grading System', defaultInputs: { marks: 88 } },
  { id: 11, title: '11. Factorial Computation', defaultInputs: { n: 6 } },
  { id: 12, title: '12. Multiplication Table', defaultInputs: { n: 8, limit: 10 } },
  { id: 13, title: '13. Sum of Natural Numbers', defaultInputs: { n: 50 } },
  { id: 14, title: '14. Fibonacci Sequence', defaultInputs: { n: 10 } },
  { id: 15, title: '15. Count Digits', defaultInputs: { n: 987654 } },
  { id: 16, title: '16. Reverse a Number', defaultInputs: { n: 12345 } },
  { id: 17, title: '17. Palindrome Number', defaultInputs: { n: 12321 } },
  { id: 18, title: '18. Prime Number Checker', defaultInputs: { n: 31 } },
  { id: 19, title: '19. Armstrong Number', defaultInputs: { n: 153 } },
  { id: 20, title: '20. Vowel or Consonant', defaultInputs: { char: 'e' } },
  { id: 21, title: '21. List Elements Sum', defaultInputs: { numbers: [10, 20, 30, 40] } },
  { id: 22, title: '22. Find Min and Max in List', defaultInputs: { numbers: [45, 12, 89, 3, 67] } },
  { id: 23, title: '23. Count Elements Frequency', defaultInputs: { numbers: [1, 2, 3, 2, 4, 2], target: 2 } },
  { id: 24, title: '24. String Reversal', defaultInputs: { text: 'NIVARA Caregiver' } },
  { id: 25, title: '25. Count Vowels in String', defaultInputs: { text: 'Autism Spectrum Support' } },
  { id: 26, title: '26. Length of String (Custom)', defaultInputs: { text: 'Hello World' } },
  { id: 27, title: '27. Pattern Printing - Square', defaultInputs: { size: 5 } },
  { id: 28, title: '28. Pattern Printing - Right Triangle', defaultInputs: { rows: 5 } },
  { id: 29, title: '29. List De-duplication', defaultInputs: { numbers: [1, 2, 2, 3, 4, 3, 5] } },
  { id: 30, title: '30. Even Numbers in a Range', defaultInputs: { lower: 10, upper: 30 } },
];

export default function ProgramRunnerScreen({ navigation }) {
  const wsUrl = `${WS_URL.replace('http', 'ws')}/v1/community/ws/programs`;
  const { isReady, val, sendData } = useWebSocket(wsUrl);

  const [selectedProgram, setSelectedProgram] = useState(PROGRAM_LIST[0]);
  const [inputJsonText, setInputJsonText] = useState(JSON.stringify(PROGRAM_LIST[0].defaultInputs, null, 2));
  const [history, setHistory] = useState([]);

  const handleSelectProgram = (prog) => {
    setSelectedProgram(prog);
    setInputJsonText(JSON.stringify(prog.defaultInputs, null, 2));
  };

  const handleExecute = () => {
    let parsedInputs = {};
    try {
      parsedInputs = JSON.parse(inputJsonText);
    } catch (e) {
      alert("Invalid JSON format in inputs!");
      return;
    }

    const payload = {
      type: "run_program",
      program_id: selectedProgram.id,
      inputs: parsedInputs,
    };

    sendData(payload);
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation?.goBack?.()}>
          <Text style={styles.backBtnText}>‹ Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>WebSocket Task Runner</Text>
        <View style={styles.statusBadge}>
          <Text style={[styles.statusText, { color: isReady ? '#10B981' : '#EF4444' }]}>
            {isReady ? 'Connected 🟢' : 'Disconnected 🔴'}
          </Text>
        </View>
      </View>

      <ScrollView style={styles.content} keyboardShouldPersistTaps="handled">
        {/* Program Selection Grid */}
        <Text style={styles.sectionTitle}>Select Program (1 - 30)</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.progPickerScroll}>
          {PROGRAM_LIST.map((prog) => {
            const isSelected = prog.id === selectedProgram.id;
            return (
              <TouchableOpacity
                key={prog.id}
                style={[styles.progCard, isSelected && styles.progCardActive]}
                onPress={() => handleSelectProgram(prog)}
              >
                <Text style={[styles.progCardText, isSelected && styles.progCardTextActive]}>
                  #{prog.id}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        <View style={styles.selectedMeta}>
          <Text style={styles.selectedTitle}>{selectedProgram.title}</Text>
        </View>

        {/* Input Editor */}
        <Text style={styles.sectionTitle}>Program Parameters (JSON)</Text>
        <TextInput
          style={styles.jsonInput}
          multiline
          numberOfLines={5}
          value={inputJsonText}
          onChangeText={setInputJsonText}
          autoCapitalize="none"
          autoCorrect={false}
        />

        {/* Execute Button */}
        <TouchableOpacity
          style={[styles.executeBtn, !isReady && styles.executeBtnDisabled]}
          onPress={handleExecute}
          disabled={!isReady}
        >
          <Text style={styles.executeBtnText}>
            ⚡ Run #{selectedProgram.id} over WebSocket
          </Text>
        </TouchableOpacity>

        {/* Real-Time WebSocket Output */}
        <Text style={styles.sectionTitle}>Latest WebSocket Response</Text>
        <View style={styles.responseCard}>
          {val ? (
            <View>
              <Text style={styles.respHeader}>
                {val.data?.title || 'Execution Result'} {val.data?.success ? '✅' : '❌'}
              </Text>
              <Text style={styles.respMessage}>
                {val.message || val.data?.result || JSON.stringify(val)}
              </Text>
              {val.data?.details && (
                <Text style={styles.respDetails}>
                  Details: {JSON.stringify(val.data.details, null, 2)}
                </Text>
              )}
            </View>
          ) : (
            <Text style={styles.placeholderText}>
              No output yet. Click "Run" to send payload over WebSocket.
            </Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  backBtn: {
    padding: 4,
  },
  backBtnText: {
    fontSize: 16,
    color: '#0F172A',
    fontWeight: '600',
  },
  headerTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#0F172A',
  },
  statusBadge: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  content: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#64748B',
    marginBottom: 8,
    marginTop: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  progPickerScroll: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  progCard: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 10,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    marginRight: 8,
  },
  progCardActive: {
    backgroundColor: '#3B82F6',
    borderColor: '#3B82F6',
  },
  progCardText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#334155',
  },
  progCardTextActive: {
    color: '#FFFFFF',
  },
  selectedMeta: {
    backgroundColor: '#EFF6FF',
    padding: 12,
    borderRadius: 10,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#3B82F6',
  },
  selectedTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1E40AF',
  },
  jsonInput: {
    backgroundColor: '#1E293B',
    color: '#38BDF8',
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
    fontSize: 14,
    padding: 12,
    borderRadius: 10,
    marginBottom: 16,
  },
  executeBtn: {
    backgroundColor: '#10B981',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#10B981',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 3,
  },
  executeBtnDisabled: {
    backgroundColor: '#9CA3AF',
  },
  executeBtnText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  responseCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    minHeight: 120,
    marginBottom: 32,
  },
  respHeader: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
    marginBottom: 8,
  },
  respMessage: {
    fontSize: 15,
    color: '#334155',
    lineHeight: 22,
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
    backgroundColor: '#F8FAFC',
    padding: 10,
    borderRadius: 8,
    marginBottom: 8,
  },
  respDetails: {
    fontSize: 12,
    color: '#64748B',
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
  },
  placeholderText: {
    color: '#94A3B8',
    fontSize: 14,
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 30,
  },
});
