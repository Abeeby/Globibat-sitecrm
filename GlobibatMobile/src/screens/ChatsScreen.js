import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  FlatList,
} from 'react-native';
import {
  TextInput,
  IconButton,
  List,
  Avatar,
  Surface,
  Chip,
  ActivityIndicator,
} from 'react-native-paper';
import { useSocket } from '../contexts/SocketContext';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';
import moment from 'moment';
import 'moment/locale/fr';

moment.locale('fr');

export default function ChatsScreen() {
  const [message, setMessage] = useState('');
  const [currentRoom, setCurrentRoom] = useState('general');
  const scrollViewRef = useRef();
  const { user } = useAuth();
  const {
    connected,
    messages,
    typingUsers,
    joinChat,
    sendMessage,
    sendTyping,
  } = useSocket();

  useEffect(() => {
    if (connected) {
      joinChat(currentRoom);
    }
  }, [connected, currentRoom]);

  const handleSend = () => {
    if (message.trim() && connected) {
      sendMessage(currentRoom, message);
      setMessage('');
    }
  };

  const handleTyping = (text) => {
    setMessage(text);
    if (connected) {
      sendTyping(currentRoom, text.length > 0);
    }
  };

  const roomMessages = messages[currentRoom] || [];

  const renderMessage = ({ item }) => {
    const isOwn = item.user_id === user?.id;
    
    return (
      <View style={[styles.messageContainer, isOwn && styles.ownMessageContainer]}>
        {!isOwn && (
          <Avatar.Text
            size={32}
            label={item.user?.substring(0, 2).toUpperCase()}
            style={styles.avatar}
          />
        )}
        <Surface style={[styles.messageBubble, isOwn && styles.ownMessageBubble]}>
          {!isOwn && <Text style={styles.messageUser}>{item.user}</Text>}
          <Text style={[styles.messageText, isOwn && styles.ownMessageText]}>
            {item.message}
          </Text>
          <Text style={[styles.messageTime, isOwn && styles.ownMessageTime]}>
            {moment(item.time).format('HH:mm')}
          </Text>
        </Surface>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
      keyboardVerticalOffset={90}
    >
      {/* Header */}
      <Surface style={styles.header}>
        <View style={styles.headerContent}>
          <Text style={styles.roomName}>Chat {currentRoom}</Text>
          <Chip
            icon="wifi"
            style={[
              styles.statusChip,
              { backgroundColor: connected ? config.colors.success : config.colors.danger }
            ]}
            textStyle={{ color: 'white', fontSize: 10 }}
          >
            {connected ? 'En ligne' : 'Hors ligne'}
          </Chip>
        </View>
        {typingUsers[currentRoom] && (
          <Text style={styles.typingIndicator}>
            {typingUsers[currentRoom]} est en train d'écrire...
          </Text>
        )}
      </Surface>

      {/* Messages */}
      <FlatList
        ref={scrollViewRef}
        data={roomMessages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id || Math.random().toString()}
        contentContainerStyle={styles.messagesList}
        onContentSizeChange={() => scrollViewRef.current?.scrollToEnd()}
      />

      {/* Input */}
      <Surface style={styles.inputContainer}>
        <TextInput
          value={message}
          onChangeText={handleTyping}
          placeholder="Tapez votre message..."
          mode="outlined"
          style={styles.input}
          disabled={!connected}
          right={
            <TextInput.Icon
              icon="send"
              onPress={handleSend}
              disabled={!message.trim() || !connected}
            />
          }
        />
      </Surface>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: config.colors.light,
  },
  header: {
    padding: 12,
    elevation: 2,
    backgroundColor: 'white',
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  roomName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: config.colors.dark,
  },
  statusChip: {
    height: 24,
  },
  typingIndicator: {
    fontSize: 12,
    color: config.colors.dark,
    opacity: 0.6,
    fontStyle: 'italic',
    marginTop: 4,
  },
  messagesList: {
    padding: 16,
  },
  messageContainer: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'flex-end',
  },
  ownMessageContainer: {
    justifyContent: 'flex-end',
  },
  avatar: {
    marginRight: 8,
  },
  messageBubble: {
    maxWidth: '75%',
    padding: 12,
    borderRadius: 16,
    elevation: 1,
  },
  ownMessageBubble: {
    backgroundColor: config.colors.primary,
  },
  messageUser: {
    fontSize: 12,
    fontWeight: 'bold',
    color: config.colors.primary,
    marginBottom: 4,
  },
  messageText: {
    fontSize: 14,
    color: config.colors.dark,
  },
  ownMessageText: {
    color: 'white',
  },
  messageTime: {
    fontSize: 10,
    color: config.colors.dark,
    opacity: 0.5,
    marginTop: 4,
  },
  ownMessageTime: {
    color: 'white',
    opacity: 0.8,
  },
  inputContainer: {
    padding: 8,
    elevation: 4,
    backgroundColor: 'white',
  },
  input: {
    backgroundColor: 'white',
  },
});