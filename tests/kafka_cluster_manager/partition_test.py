import pytest
from mock import Mock
from mock import sentinel

from yelp_kafka_tool.kafka_cluster_manager.cluster_info.broker import Broker
from yelp_kafka_tool.kafka_cluster_manager.cluster_info.partition import Partition


class TestPartition(object):

    @pytest.fixture
    def partition(self):
        mock_topic = sentinel.t1
        mock_topic.id = 't1'
        return Partition(
            mock_topic,
            0,
            [sentinel.r1, sentinel.r2],
        )

    def test_name(self, partition):
        assert partition.name == ('t1', 0)

    def test_topic(self, partition):
        assert partition.topic == sentinel.t1

    def test_replicas(self, partition):
        assert partition.replicas == [sentinel.r1, sentinel.r2]

    def test_leader(self, partition):
        assert partition.leader == sentinel.r1

    def test_replication_factor(self, partition):
        assert partition.replication_factor == 2

    def test_partition_id(self, partition):
        assert partition.partition_id == 0

    def test_add_replica(self, partition):
        new_broker = sentinel.new_r
        partition.add_replica(new_broker)
        assert partition.replicas == [sentinel.r1, sentinel.r2, sentinel.new_r]

    def test_swap_leader(self, partition):
        b = sentinel.r2
        old_replicas = partition.replicas
        partition.swap_leader(b)

        # Verify leader changed to b
        assert partition.leader == b
        # Verify that replica set remains same
        assert sorted(old_replicas) == sorted(partition.replicas)

    def test_followers_1(self, partition):
        # Case:1 With followers
        assert partition.followers == [sentinel.r2]

    def test_followers_2(self):
        # Case:2 No-followers
        mock_topic = sentinel.t1
        mock_topic.id = 't1'
        p2 = Partition(mock_topic, 0, [sentinel.r1])

        assert p2.followers == []

    def test_count_siblings(self):
        t1, t1.id = sentinel.t1, 't1'
        t2, t2.id = sentinel.t2, 't2'
        p1, p3, p4 = Partition(t1, 0), Partition(t1, 1), Partition(t2, 0),

        # verify sibling count
        p_group = [p1, p4, p3]
        assert p3.count_siblings(p_group) == 2
        assert p4.count_siblings(p_group) == 1
        p_group = [p4]
        assert p1.count_siblings(p_group) == 0

        # Empty group
        p_group = []
        assert p1.count_siblings(p_group) == 0

    def test_has_inactive_replicas_all_active(self):
        topic = Mock()
        partition = Partition(topic, 0, [Broker('b1'), Broker('b2')])

        assert partition.has_inactive_replicas() is False

    def test_has_inactive_replicas_inactive(self):
        topic = Mock()
        inactive = Broker('b3')
        inactive.mark_inactive()
        partition = Partition(topic, 0, [Broker('b1'), Broker('b2'), inactive])

        assert partition.has_inactive_replicas() is True
